import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import logging
from logger import sim_logger

class DemandForecaster:
    def __init__(self, demand_mean=20):
        self.demand_mean = demand_mean
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        
    def generate_synthetic_data(self, days=730):
        """Generate 2 years of synthetic historical sales data with weekly seasonality."""
        sim_logger.info("Generating synthetic historical data for ML model...")
        np.random.seed(42) # For reproducibility
        data = []
        for day in range(days):
            day_of_week = day % 7
            # Weekends (5, 6) have higher demand
            if day_of_week >= 5:
                base = self.demand_mean * 1.5
            else:
                base = self.demand_mean * 0.8
                
            # Add Poisson noise
            actual_demand = np.random.poisson(base)
            data.append({
                'day': day,
                'day_of_week': day_of_week,
                'demand': actual_demand
            })
            
        return pd.DataFrame(data)
        
    def train(self):
        """Train the Random Forest model on synthetic data."""
        df = self.generate_synthetic_data()
        X = df[['day_of_week']]
        y = df['demand']
        
        sim_logger.info("Training Random Forest Regressor...")
        # Suppress sklearn warnings about feature names if needed
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        self.model.fit(X, y)
        self.is_trained = True
        sim_logger.info("ML Model trained successfully.")
        
    def predict(self, current_day):
        """Predict demand for the given day."""
        if not self.is_trained:
            self.train()
            
        day_of_week = current_day % 7
        pred = self.model.predict([[day_of_week]])[0]
        return max(0, int(np.round(pred)))

# Global instance for the simulation
forecaster = DemandForecaster()
