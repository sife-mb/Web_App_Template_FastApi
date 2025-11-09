import { useSession, signIn, signOut } from "next-auth/react";
// useState und DummyChart sind nicht mehr nötig, wenn der Backend-Test weg ist
import { useEffect, useState } from "react"; 
import Layout from "../components/Layout";

// Dies ist deine Hauptseite (http://localhost:3000)

export default function Home() {
  console.log("Rendering Home page");
  const { data: session, status } = useSession();
  console.log(session);

  // --- State für die Live-Daten aus InfluxDB ---
  const [influxData, setInfluxData] = useState(null);

  // --- KORRIGIERTER HOOK FÜR LIVE-DATEN-POLLING ---
  useEffect(() => {
    
    // 1. Definiere die Funktion, die die Daten holt
    const fetchInfluxData = async () => {
      try {
        // --- KORRIGIERTE URL: Fest einprogrammiert für den Test ---
        const apiUrl = "http://localhost:8001";
        const res = await fetch(`${apiUrl}/api/influx-raw-data`);
        // --- ENDE DER ÄNDERUNG ---

        const data = await res.json();
        
        if (!res.ok) {
          console.error("Influx-Poll-Fehler:", data.detail || "Fehler beim Influx-Polling");
          setInfluxData({ error: data.detail });
        } else {
          // --- HIER IST DEIN KONSOLEN-LOG ---
          console.log("Live-Daten (Poll) erfolgreich empfangen:", data);
          setInfluxData(data);
        }
      } catch (e) {
        console.error("Influx-Poll-Fetch-Fehler:", e.message);
        setInfluxData({ error: e.message });
      }
    };

    // 2. Prüfe, ob wir eingeloggt sind
    if (status === "authenticated") {
      // 3. Wenn ja, starte das Polling
      
      // Führe es einmal sofort aus
      fetchInfluxData(); 
      
      // Starte das Intervall (speichere die ID)
      const intervalId = setInterval(fetchInfluxData, 5000);

      // 4. Wichtig: Definiere die Aufräum-Funktion
      // Diese wird aufgerufen, wenn der Hook neu läuft (z.B. beim Logout)
      return () => {
        clearInterval(intervalId);
        console.log("Polling gestoppt.");
      };
    }
    
  // 5. ABHÄNGIGKEIT: Führe diesen ganzen Hook-Code jedes Mal neu aus,
  //    wenn sich der 'status' (z.B. von loading -> authenticated) ändert.
  }, [status]); 

  // --- ENDE DES POLLING-HOOKS ---

  console.log("Rendering Home page");
  console.log(session);


  // Lade-Status anzeigen, während die Session geprüft wird
  if (status === "loading") {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <p className="text-xl">Lade...</p>
        </div>
      </Layout>
    );
  }

  // Wenn der Benutzer NICHT eingeloggt ist, zeige den Login-Bildschirm
  if (!session) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center text-center p-8">
          <h1 className="text-2xl font-bold mb-4 text-cyan-400">
            Willkommen zum SMART CAMPUS
          </h1>
          <p className="mb-6">Bitte melden Sie sich an, um das Dashboard zu sehen.</p>
          <button
            onClick={() => signIn()} // Startet den Keycloak-Login
            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-md font-semibold transition-all"
          >
            Anmelden
          </button>
        </div>
      </Layout>
    );
  }

  // Wenn der Benutzer eingeloggt IST, zeige das volle Dashboard
  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">SMART CAMPUS</h1>
          <h2 className="text-lg text-gray-400">
            Angemeldet als:{" "}
            <strong className="text-green-400">
              {session.user.name || session.user.email}
            </strong>
          </h2>
        </div>
        <button
          onClick={() => signOut()} // Startet den Logout
          className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-md font-semibold transition-all"
        >
          Abmelden
        </button>
      </div>

      {/* Dashboard-Inhalt */}
      <div className="mb-8">
        <h2 className="text-lg mb-2">Willkommen zum SMART CAMPUS Dashboard!</h2>
        {/* <DummyChart /> */}
        {/*  */}
        
      </div>

    </Layout>
  );
}

