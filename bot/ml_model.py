"""
Machine Learning model for price prediction
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
import logging

try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    logging.warning("TensorFlow/Keras not available. ML model will use fallback predictions.")

from config.settings import (
    EPOCHS, BATCH_SIZE, LSTM_UNITS, DROPOUT_RATE,
    TRAIN_TEST_SPLIT, VALIDATION_SPLIT, MODEL_PATH
)


class LSTMPredictor:
    """LSTM Neural Network for stock price prediction"""
    
    def __init__(self, lookback: int = 60):
        """
        Initialize LSTM predictor
        
        Args:
            lookback: Number of days to use for prediction
        """
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def prepare_data(self, data: pd.Series, lookback: int = None) -> tuple:
        """
        Prepare data for LSTM training
        
        Args:
            data: Price series
            lookback: Days to look back
            
        Returns:
            Tuple of (X, y) arrays
        """
        if lookback is None:
            lookback = self.lookback
        
        scaled_data = self.scaler.fit_transform(data.values.reshape(-1, 1))
        
        X, y = [], []
        for i in range(len(scaled_data) - lookback):
            X.append(scaled_data[i:i+lookback])
            y.append(scaled_data[i+lookback])
        
        return np.array(X), np.array(y)
    
    def build_model(self) -> Sequential:
        """
        Build LSTM model
        
        Returns:
            Compiled Keras model
        """
        if not KERAS_AVAILABLE:
            self.logger.warning("Keras not available, model will not be built")
            return None
        
        model = Sequential([
            LSTM(LSTM_UNITS, activation='relu', input_shape=(self.lookback, 1), return_sequences=True),
            Dropout(DROPOUT_RATE),
            LSTM(LSTM_UNITS, activation='relu', return_sequences=False),
            Dropout(DROPOUT_RATE),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def train(self, data: pd.Series, epochs: int = EPOCHS, batch_size: int = BATCH_SIZE) -> dict:
        """
        Train the LSTM model
        
        Args:
            data: Historical price data
            epochs: Number of epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if not KERAS_AVAILABLE:
            self.logger.warning("Keras not available, skipping training")
            return {'loss': 0}
        
        X, y = self.prepare_data(data)
        
        split_idx = int(len(X) * TRAIN_TEST_SPLIT)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        self.model = self.build_model()
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=VALIDATION_SPLIT,
            verbose=0
        )
        
        # Evaluate on test set
        test_loss = self.model.evaluate(X_test, y_test, verbose=0)
        self.logger.info(f"Test loss: {test_loss}")
        
        return history.history
    
    def predict_next(self, data: pd.Series) -> float:
        """
        Predict next day's price
        
        Args:
            data: Historical price data
            
        Returns:
            Predicted price (unscaled)
        """
        if not KERAS_AVAILABLE or self.model is None:
            # Fallback: Simple moving average prediction
            return float(data.iloc[-1])
        
        scaled_data = self.scaler.fit_transform(data.values.reshape(-1, 1))
        
        if len(scaled_data) < self.lookback:
            return float(data.iloc[-1])
        
        last_data = scaled_data[-self.lookback:].reshape(1, self.lookback, 1)
        scaled_prediction = self.model.predict(last_data, verbose=0)
        
        prediction = self.scaler.inverse_transform(scaled_prediction)[0][0]
        return float(prediction)
    
    def predict_sequence(self, data: pd.Series, days: int = 5) -> np.ndarray:
        """
        Predict multiple days ahead
        
        Args:
            data: Historical price data
            days: Number of days to predict
            
        Returns:
            Array of predictions
        """
        if not KERAS_AVAILABLE or self.model is None:
            # Fallback: Return last price
            return np.full(days, float(data.iloc[-1]))
        
        predictions = []
        current_data = data.copy()
        
        for _ in range(days):
            next_pred = self.predict_next(current_data)
            predictions.append(next_pred)
            current_data = pd.concat([current_data, pd.Series([next_pred])])
        
        return np.array(predictions)
    
    def save_model(self, path: str = MODEL_PATH):
        """Save model to disk"""
        if self.model is None or not KERAS_AVAILABLE:
            return
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        self.logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = MODEL_PATH):
        """Load model from disk"""
        if not KERAS_AVAILABLE:
            return
        
        if os.path.exists(path):
            self.model = load_model(path)
            self.logger.info(f"Model loaded from {path}")
        else:
            self.logger.warning(f"Model not found at {path}")


class SimplePredictor:
    """Simple fallback predictor using moving averages"""
    
    @staticmethod
    def predict_next(data: pd.Series, lookback: int = 20) -> float:
        """
        Predict next price using exponential moving average
        
        Args:
            data: Historical price data
            lookback: Number of days for EMA
            
        Returns:
            Predicted price
        """
        if len(data) < lookback:
            return float(data.iloc[-1])
        
        ema = data.ewm(span=lookback).mean()
        return float(ema.iloc[-1])
    
    @staticmethod
    def calculate_trend(data: pd.Series, lookback: int = 20) -> str:
        """
        Calculate price trend
        
        Args:
            data: Historical price data
            lookback: Number of days for trend
            
        Returns:
            'up', 'down', or 'sideways'
        """
        if len(data) < lookback:
            return 'sideways'
        
        recent = data.iloc[-lookback:]
        if recent.iloc[-1] > recent.iloc[-lookback//2]:
            return 'up'
        elif recent.iloc[-1] < recent.iloc[-lookback//2]:
            return 'down'
        else:
            return 'sideways'
