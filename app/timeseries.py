import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

def decompose_time_series(series: pd.Series, period: int = 30, model: str = 'additive'):
    """
    Decomposes a time series into its seasonal, trend, and residual components.

    Parameters:
    series (pd.Series): The time series data to decompose.
    period (int): The number of periods in a complete seasonal cycle.
    model (str): The type of seasonal component. Either 'additive' or 'multiplicative'.

    Returns:
    dict: A dictionary containing the seasonal, trend, and residual components.
    """
    decomposition = seasonal_decompose(series, model=model, period=period)
    
    return {
        'seasonal': decomposition.seasonal,
        'trend': decomposition.trend,
        'residual': decomposition.resid,
        'observed': decomposition.observed
    }

def generate_dummy_timeseries():
    # Dummy-Zeitreihe erzeugen
    np.random.seed(42)
    date_rng = pd.date_range(start='2023-01-01', periods=100, freq='D')

    trend = np.linspace(10, 20, 100)                              # linearer Trend
    seasonal = 2 * np.sin(2 * np.pi * date_rng.dayofyear / 30)    # Monatszyklus
    noise = np.random.normal(0, 0.5, 100)                         # Rauschen

    series = pd.Series(trend + seasonal + noise, index=date_rng)

    # Dekomposition
    result = seasonal_decompose(series, model="additive", period=30)

    # Plot
    result.plot()
    plt.show()