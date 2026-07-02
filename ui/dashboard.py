"""
Flask web dashboard for trading bot monitoring
"""
import logging
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime

from bot.portfolio import Portfolio
from bot.trading_engine import TradingEngine
from api.data_fetcher import DataFetcher
from config.settings import FLASK_HOST, FLASK_PORT, DEBUG


class TradingDashboard:
    """Web dashboard for trading bot"""
    
    def __init__(self, trading_engine: TradingEngine = None):
        # Get absolute path for templates and static files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, 'ui', 'templates')
        static_dir = os.path.join(base_dir, 'ui', 'static')
        
        self.app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        CORS(self.app)
        
        self.trading_engine = trading_engine or TradingEngine()
        self.data_fetcher = DataFetcher()
        self.logger = logging.getLogger(__name__)
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/', methods=['GET'])
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/portfolio', methods=['GET'])
        def get_portfolio():
            summary = self.trading_engine.portfolio.summary()
            return jsonify(summary)
        
        @self.app.route('/api/positions', methods=['GET'])
        def get_positions():
            positions = self.trading_engine.portfolio.get_positions()
            return jsonify(positions)
        
        @self.app.route('/api/signal/<symbol>', methods=['GET'])
        def get_signal(symbol):
            try:
                data = self.data_fetcher.fetch_historical_data(symbol, interval='1d')
                if data.empty:
                    return jsonify({'error': f'No data for {symbol}'}), 404
                
                signal = self.trading_engine.generate_signal(symbol, data)
                return jsonify(signal)
            except Exception as e:
                self.logger.error(f"Error generating signal: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/price/<symbol>', methods=['GET'])
        def get_price(symbol):
            try:
                price = self.data_fetcher.get_current_price(symbol)
                if price:
                    return jsonify({'symbol': symbol, 'price': float(price)})
                return jsonify({'error': 'Price not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def run(self, host: str = FLASK_HOST, port: int = FLASK_PORT, debug: bool = DEBUG):
        """Run the dashboard"""
        self.logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
