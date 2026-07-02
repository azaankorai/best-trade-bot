"""
Portfolio management and tracking
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

from config.settings import INITIAL_CAPITAL, RISK_PER_TRADE, MAX_POSITIONS


class Portfolio:
    """Manage trading portfolio"""
    
    def __init__(self, initial_capital: float = INITIAL_CAPITAL):
        """
        Initialize portfolio
        
        Args:
            initial_capital: Starting capital in dollars
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, dict] = {}  # symbol -> {shares, avg_cost, current_price}
        self.trades: List[dict] = []
        self.logger = logging.getLogger(__name__)
    
    def get_total_value(self) -> float:
        """
        Calculate total portfolio value
        
        Returns:
            Total value in dollars
        """
        position_value = sum(
            pos['shares'] * pos['current_price']
            for pos in self.positions.values()
        )
        return self.cash + position_value
    
    def get_portfolio_return(self) -> float:
        """
        Calculate portfolio return percentage
        
        Returns:
            Return as percentage
        """
        total_value = self.get_total_value()
        return ((total_value - self.initial_capital) / self.initial_capital) * 100
    
    def buy(self, symbol: str, shares: int, price: float, 
            timestamp: datetime = None) -> bool:
        """
        Buy stock
        
        Args:
            symbol: Stock symbol
            shares: Number of shares
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            True if successful, False otherwise
        """
        cost = shares * price
        
        if cost > self.cash:
            self.logger.warning(f"Insufficient funds to buy {shares} shares of {symbol}")
            return False
        
        if len(self.positions) >= MAX_POSITIONS and symbol not in self.positions:
            self.logger.warning(f"Maximum positions ({MAX_POSITIONS}) reached")
            return False
        
        if symbol in self.positions:
            # Add to existing position
            pos = self.positions[symbol]
            total_shares = pos['shares'] + shares
            total_cost = (pos['shares'] * pos['avg_cost']) + cost
            pos['avg_cost'] = total_cost / total_shares
            pos['shares'] = total_shares
        else:
            # Create new position
            self.positions[symbol] = {
                'shares': shares,
                'avg_cost': price,
                'current_price': price,
                'buy_date': timestamp or datetime.now()
            }
        
        self.cash -= cost
        
        self.trades.append({
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'total': cost,
            'timestamp': timestamp or datetime.now(),
            'portfolio_value': self.get_total_value()
        })
        
        self.logger.info(f"Bought {shares} shares of {symbol} at ${price:.2f}")
        return True
    
    def sell(self, symbol: str, shares: int, price: float,
            timestamp: datetime = None) -> bool:
        """
        Sell stock
        
        Args:
            symbol: Stock symbol
            shares: Number of shares
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if symbol not in self.positions:
            self.logger.warning(f"No position in {symbol}")
            return False
        
        pos = self.positions[symbol]
        
        if shares > pos['shares']:
            self.logger.warning(f"Insufficient shares of {symbol}")
            return False
        
        revenue = shares * price
        self.cash += revenue
        
        # Calculate profit/loss
        cost_basis = shares * pos['avg_cost']
        profit = revenue - cost_basis
        profit_pct = (profit / cost_basis) * 100 if cost_basis > 0 else 0
        
        if shares == pos['shares']:
            # Close entire position
            del self.positions[symbol]
        else:
            # Reduce position size
            pos['shares'] -= shares
        
        self.trades.append({
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'total': revenue,
            'profit': profit,
            'profit_pct': profit_pct,
            'timestamp': timestamp or datetime.now(),
            'portfolio_value': self.get_total_value()
        })
        
        self.logger.info(f"Sold {shares} shares of {symbol} at ${price:.2f} "
                        f"(Profit: ${profit:.2f} / {profit_pct:.2f}%)")
        return True
    
    def update_prices(self, prices: Dict[str, float]):
        """
        Update current prices for all positions
        
        Args:
            prices: Dictionary of symbol -> price
        """
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol]['current_price'] = price
    
    def get_position(self, symbol: str) -> Optional[dict]:
        """
        Get position details
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Position dictionary or None
        """
        return self.positions.get(symbol)
    
    def get_positions(self) -> Dict[str, dict]:
        """Get all positions"""
        return self.positions.copy()
    
    def get_trades(self) -> List[dict]:
        """Get trade history"""
        return self.trades.copy()
    
    def calculate_returns(self) -> dict:
        """
        Calculate portfolio returns
        
        Returns:
            Dictionary with return metrics
        """
        if not self.trades:
            return {
                'total_return': 0,
                'total_return_pct': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        sold_trades = [t for t in self.trades if t['action'] == 'SELL']
        
        if not sold_trades:
            return {
                'total_return': 0,
                'total_return_pct': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        profits = [t.get('profit', 0) for t in sold_trades]
        total_profit = sum(profits)
        
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        
        return {
            'total_return': total_profit,
            'total_return_pct': self.get_portfolio_return(),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(sold_trades) * 100 if sold_trades else 0,
            'avg_win': sum(wins) / len(wins) if wins else 0,
            'avg_loss': abs(sum(losses) / len(losses)) if losses else 0,
            'largest_win': max(wins) if wins else 0,
            'largest_loss': min(losses) if losses else 0
        }
    
    def get_sharpe_ratio(self, daily_returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            daily_returns: Series of daily returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if len(daily_returns) < 2:
            return 0
        
        excess_returns = daily_returns.mean() - (risk_free_rate / 252)
        std_returns = daily_returns.std()
        
        if std_returns == 0:
            return 0
        
        sharpe = (excess_returns / std_returns) * np.sqrt(252)
        return float(sharpe)
    
    def get_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown
        
        Returns:
            Maximum drawdown as percentage
        """
        if not self.trades:
            return 0
        
        portfolio_values = [t['portfolio_value'] for t in self.trades]
        
        max_val = portfolio_values[0]
        max_drawdown = 0
        
        for val in portfolio_values:
            if val > max_val:
                max_val = val
            drawdown = (max_val - val) / max_val
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown * 100
    
    def summary(self) -> dict:
        """
        Get portfolio summary
        
        Returns:
            Summary dictionary
        """
        returns = self.calculate_returns()
        
        return {
            'total_value': self.get_total_value(),
            'cash': self.cash,
            'positions': len(self.positions),
            'total_return': returns['total_return'],
            'total_return_pct': returns['total_return_pct'],
            'win_rate': returns['win_rate'],
            'trades': len(self.trades),
            'max_drawdown': self.get_max_drawdown()
        }


import numpy as np
