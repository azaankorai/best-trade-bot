"""
Vercel Serverless Function - Trading Bot API & Dashboard
Includes both API endpoints and HTML dashboard
"""
from flask import Flask, jsonify, render_template_string
import json

app = Flask(__name__)

# HTML Dashboard Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Best Trade Bot - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #212121;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 14px;
        }
        
        .status .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #4caf50;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .dashboard {
            padding: 30px;
        }
        
        section {
            margin-bottom: 40px;
        }
        
        section h2 {
            color: #1e88e5;
            margin-bottom: 20px;
            border-bottom: 2px solid #f5f5f5;
            padding-bottom: 10px;
            font-size: 20px;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #1e88e5;
            text-align: center;
        }
        
        .metric-card label {
            display: block;
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .metric-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #1e88e5;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            overflow: hidden;
        }
        
        table thead {
            background: #1e88e5;
            color: white;
        }
        
        table th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        
        table tbody tr:hover {
            background: #f0f0f0;
        }
        
        .signal-section {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
        }
        
        .signal-input {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .signal-input input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .signal-input button {
            padding: 10px 30px;
            background: #1e88e5;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .signal-input button:hover {
            background: #1565c0;
        }
        
        .signal-result {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-left: 4px solid #1e88e5;
            border-radius: 4px;
        }
        
        .signal-result .buy {
            color: #43a047;
            font-weight: bold;
        }
        
        .signal-result .sell {
            color: #e53935;
            font-weight: bold;
        }
        
        .signal-result .hold {
            color: #fb8c00;
            font-weight: bold;
        }
        
        footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
        
        .api-status {
            background: #e8f5e9;
            border: 1px solid #4caf50;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Best Trade Bot</h1>
            <div class="status">
                <span class="dot"></span> Live & Running
            </div>
        </header>
        
        <div class="dashboard">
            <div class="api-status">
                ✅ API is working correctly. Dashboard features coming soon with real data integration.
            </div>
            
            <section>
                <h2>Portfolio Overview</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <label>Total Value</label>
                        <div class="value">$10,000.00</div>
                    </div>
                    <div class="metric-card">
                        <label>Cash Available</label>
                        <div class="value">$10,000.00</div>
                    </div>
                    <div class="metric-card">
                        <label>Return %</label>
                        <div class="value">0.00%</div>
                    </div>
                    <div class="metric-card">
                        <label>Win Rate</label>
                        <div class="value">0%</div>
                    </div>
                </div>
            </section>
            
            <section>
                <h2>Active Positions</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Shares</th>
                            <th>Avg Cost</th>
                            <th>Current Price</th>
                            <th>P&L</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="5" style="text-align: center; color: #999;">No open positions</td>
                        </tr>
                    </tbody>
                </table>
            </section>
            
            <section class="signal-section">
                <h2>Get Trading Signal</h2>
                <div class="signal-input">
                    <input type="text" id="symbolInput" placeholder="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)..." value="AAPL">
                    <button onclick="getSignal()">Get Signal</button>
                </div>
                <div id="signalResult"></div>
            </section>
            
            <section>
                <h2>API Endpoints</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Endpoint</th>
                            <th>Method</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>/</td>
                            <td>GET</td>
                            <td>Dashboard home page</td>
                        </tr>
                        <tr>
                            <td>/api/health</td>
                            <td>GET</td>
                            <td>API health check</td>
                        </tr>
                        <tr>
                            <td>/api/portfolio</td>
                            <td>GET</td>
                            <td>Portfolio metrics</td>
                        </tr>
                        <tr>
                            <td>/api/positions</td>
                            <td>GET</td>
                            <td>Current positions</td>
                        </tr>
                        <tr>
                            <td>/api/signal/&lt;SYMBOL&gt;</td>
                            <td>GET</td>
                            <td>Trading signal for stock</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>
        
        <footer>
            <p>Best Trade Bot © 2026 | AI-Powered Trading System</p>
            <p style="font-size: 12px; margin-top: 10px;">
                Status: ✅ API Running | Environment: Vercel Serverless
            </p>
        </footer>
    </div>
    
    <script>
        function getSignal() {
            const symbol = document.getElementById('symbolInput').value.toUpperCase();
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            fetch(`/api/signal/${symbol}`)
                .then(r => r.json())
                .then(data => {
                    const signalClass = data.signal.toLowerCase();
                    const result = `
                        <div style="padding: 15px; background: white; border-radius: 4px; border-left: 4px solid #1e88e5;">
                            <h3>${symbol}</h3>
                            <p>
                                <strong>Signal:</strong> 
                                <span class="${signalClass}">${data.signal.toUpperCase()}</span>
                            </p>
                            <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                        </div>
                    `;
                    document.getElementById('signalResult').innerHTML = result;
                })
                .catch(e => {
                    document.getElementById('signalResult').innerHTML = `<div class="signal-result">Error: ${e}</div>`;
                });
        }
        
        // Get initial signal on page load
        window.onload = function() {
            getSignal();
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """Dashboard home page"""
    try:
        return render_template_string(HTML_TEMPLATE)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'best-trade-bot',
        'version': '1.0.0'
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
    try:
        return jsonify({
            'symbol': symbol.upper(),
            'signal': 'hold',
            'confidence': 0.5,
            'price': 100.00,
            'reason': 'Neutral signal - awaiting market confirmation'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
