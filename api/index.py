"""
Vercel Serverless Function - Trading Bot API
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# Simple test routes
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Best Trade Bot API is running!', 'status': 'ok'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Best Trade Bot'})

@app.route('/api/portfolio', methods=['GET'])
def portfolio():
    return jsonify({
        'total_value': 10000,
        'cash': 10000,
        'positions': 0,
        'total_return_pct': 0,
        'win_rate': 0,
        'trades': 0,
        'max_drawdown': 0
    })

@app.route('/api/positions', methods=['GET'])
def positions():
    return jsonify({})

@app.route('/api/signal/<symbol>', methods=['GET'])
def get_signal(symbol):
    return jsonify({
        'signal': 'hold',
        'confidence': 0.5,
        'symbol': symbol,
        'price': 100.00
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500
