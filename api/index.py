"""
Vercel Serverless Function - Trading Bot API
Minimal Flask app that works on Vercel
"""
from flask import Flask, jsonify
import sys
import traceback

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    try:
        return jsonify({
            'message': 'Welcome to Best Trade Bot',
            'status': 'running',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'best-trade-bot'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def portfolio():
    """Portfolio endpoint"""
    try:
        return jsonify({
            'total_value': 10000.00,
            'cash': 10000.00,
            'positions': 0,
            'total_return_pct': 0.0,
            'win_rate': 0.0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions', methods=['GET'])
def positions():
    """Positions endpoint"""
    try:
        return jsonify({}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signal/<symbol>', methods=['GET'])
def get_signal(symbol):
    """Trading signal endpoint"""
    try:
        return jsonify({
            'symbol': symbol.upper(),
            'signal': 'hold',
            'confidence': 0.5
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
