"""
Vercel Serverless Function - Trading Bot API
Simplified Flask app for Vercel deployment
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Welcome to Best Trade Bot',
        'status': 'running',
        'version': '1.0.0'
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'best-trade-bot',
        'timestamp': 'live'
    }), 200

@app.route('/api/portfolio', methods=['GET'])
def portfolio():
    """Portfolio endpoint"""
    return jsonify({
        'total_value': 10000.00,
        'cash': 10000.00,
        'positions': 0,
        'total_return_pct': 0.0,
        'win_rate': 0.0,
        'trades': 0,
        'max_drawdown': 0.0
    }), 200

@app.route('/api/positions', methods=['GET'])
def positions():
    """Positions endpoint"""
    return jsonify({}), 200

@app.route('/api/signal/<symbol>', methods=['GET'])
def get_signal(symbol):
    """Trading signal endpoint"""
    return jsonify({
        'symbol': symbol.upper(),
        'signal': 'hold',
        'confidence': 0.5,
        'price': 100.00,
        'reason': 'Sample signal'
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price"""
    return jsonify({
        'symbol': symbol.upper(),
        'price': 100.00,
        'timestamp': 'live'
    }), 200

# For local testing
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
