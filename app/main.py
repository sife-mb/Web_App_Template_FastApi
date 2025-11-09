'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.timeseries import decompose_time_series, generate_dummy_timeseries

app = FastAPI()

# CORS für React erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/decompose")
def decompose(period: int = 30, model: str = "additive"):
    series = generate_dummy_timeseries()
    result = decompose_time_series(series, period=period, model=model)
    return result
'''

# app/main.py

import os
import requests
import time # Importiert für die Warte-Logik beim Start

# --- Imports aus deiner Datei ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# (Stelle sicher, dass diese Datei existiert: app/timeseries.py)
try:
    from app.timeseries import decompose_time_series, generate_dummy_timeseries
except ImportError:
    print("WARNUNG: app/timeseries.py nicht gefunden. Dummy-Funktionen werden erstellt.")
    # Fallback-Funktionen, damit die App nicht abstürzt
    def generate_dummy_timeseries():
        import pandas as pd
        import numpy as np
        data = np.random.rand(100)
        return pd.Series(data)
    def decompose_time_series(series, period, model):
        return {"trend": [1,2,3], "seasonal": [1,2,3], "resid": [1,2,3]}


# --- Imports für Keycloak-Authentifizierung ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, jwk
from jose.exceptions import JWTError

# --- Imports für InfluxDB ---
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


app = FastAPI()

# --- CORS für React erlauben ---
# WICHTIG: Ersetze DEINE_VM_IP mit der echten IP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://192.168.0.10:3001"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Keycloak-Konfiguration aus Umgebungsvariablen ---
KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", "http://keycloak:8080/realms/labor-projekt")
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE", "backend-client")

# --- InfluxDB-Konfiguration aus Umgebungsvariablen ---
influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "MeinSicheresInfluxToken-Labor-2025!")
influx_org = os.getenv("INFLUXDB_ORG", "labor-projekt-org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "labor-projekt-bucket")

# --- Globale Variablen für Clients ---
jwks = None
influx_query_api = None

# ====================================================================
#  ANWENDUNGS-STARTUP-LOGIK
# ====================================================================

@app.on_event("startup")
async def startup_event():
    """
    Wird beim Start von FastAPI ausgeführt.
    Lädt Keycloak-Schlüssel (mit Retries) und initialisiert InfluxDB-Client.
    """
    global jwks, influx_query_api
    
    # 1. Keycloak-Schlüssel laden (mit Warteschleife)
    retries = 10
    delay = 5  # 5 Sekunden warten
    
    print("FastAPI startet... Versuche, Keycloak-Schlüssel zu laden.")
    
    for i in range(retries):
        try:
            oidc_config_url = f"{KEYCLOAK_ISSUER}/.well-known/openid-configuration"
            oidc_config = requests.get(oidc_config_url, verify=False).json()
            jwks_uri = oidc_config.get("jwks_uri")
            jwks = requests.get(jwks_uri, verify=False).json()
            
            print(f"Öffentliche Schlüssel von Keycloak (Versuch {i+1}/{retries}) ERFOLGREICH geladen.")
            break  # Erfolg, Schleife verlassen

        except requests.exceptions.ConnectionError:
            print(f"Keycloak ist noch nicht bereit (Versuch {i+1}/{retries}). Warte {delay}s...")
            time.sleep(delay)
        
        except Exception as e:
            print(f"Unerwarteter Fehler beim Laden der Schlüssel (Versuch {i+1}/{retries}): {e}")
            time.sleep(delay)
    
    if not jwks:
        print("FEHLER: Konnte öffentliche Schlüssel von Keycloak nach mehreren Versuchen nicht laden. Auth wird fehlschlagen.")

    # 2. InfluxDB-Client initialisieren
    try:
        influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
        influx_query_api = influx_client.query_api()
        # Teste die Verbindung
        health = influx_client.health()
        if health.status == "pass":
            print("Verbindung zu InfluxDB erfolgreich hergestellt.")
        else:
            print(f"WARNUNG: InfluxDB meldet Status '{health.status}'.")
    except Exception as e:
        print(f"FEHLER: Verbindung zu InfluxDB ({influx_url}) fehlgeschlagen: {e}")


# ====================================================================
#  KEYCLOAK AUTHENTIFIZIERUNGS-LOGIK
# ====================================================================

# Schema: Erwarte einen 'Authorization: Bearer <token>'-Header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency-Funktion: Nimmt das Token, validiert es gegen Keycloak 
    und gibt den Token-Inhalt (Payload) zurück.
    """
    if not jwks:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keycloak JWKS (Schlüssel) nicht geladen. Auth-System offline."
        )

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key.get("kty"),
                    "kid": key.get("kid"),
                    "use": key.get("use"),
                    "n": key.get("n"),
                    "e": key.get("e"),
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Passender Signaturschlüssel (KID) nicht im JWKS gefunden."
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            audience=KEYCLOAK_AUDIENCE # WICHTIG: Prüft die Audience
        )
        
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ungültiges Token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler bei der Token-Validierung: {e}"
        )


# ====================================================================
#  API ENDPUNKTE
# ====================================================================

@app.get("/")
def read_root():
    """Öffentlicher Endpunkt."""
    return {"message": "Hello from FastAPI! Der Server läuft."}


@app.get("/api/decompose")
def decompose(
    period: int = 30, 
    model: str = "additive",
    # DIESE ZEILE MACHT DEN ENDPUNKT GESCHÜTZT:
    user_payload: dict = Depends(get_current_user)
):
    """
    Geschützter Endpunkt für Zeitreihen-Analyse.
    Nur gültige Token von Keycloak erhalten eine Antwort.
    """
    username = user_payload.get("preferred_username", "User")
    print(f"User '{username}' ruft /api/decompose auf.")
    
    series = generate_dummy_timeseries()
    result = decompose_time_series(series, period=period, model=model)
    return result


@app.get("/api/influx-raw-data")
def get_influx_data():
    """
    Ein öffentlicher Endpunkt, um Rohdaten von InfluxDB abzufragen.
    Holt alle Daten der letzten 24 Stunden.
    """
    if not influx_query_api:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="InfluxDB-Verbindung ist nicht konfiguriert oder fehlgeschlagen."
        )

    # Flux-Query: Alle Daten der letzten 24h aus dem Bucket
    flux_query = f"""
        from(bucket: "{influx_bucket}")
          |> range(start: -24h)
    """

    try:
        result_tables = influx_query_api.query(query=flux_query)
        
        results_json = []
        for table in result_tables:
            for record in table.records:
                results_json.append(record.values)
        print(results_json)        
        return results_json

    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler bei der InfluxDB-Abfrage: {str(e)}"
        )


@app.get("/api/protected")
def get_protected_data(user_payload: dict = Depends(get_current_user)):
    """
    Ein weiterer geschützter Endpunkt (als Beispiel).
    """
    username = user_payload.get("preferred_username", "Unbekannter User")
    
    return {
        "message": f"Hallo, {username}! Du siehst geschützte Backend-Daten.",
        "dein_token_inhalt": user_payload
    }