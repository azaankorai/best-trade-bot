#!/usr/bin/env python3
"""
Main entry point for Best Trade Bot
"""
import logging
import sys
from datetime import datetime

from bot.trading_engine import TradingEngine
from bot.portfolio import Portfolio
from api.data_fetcher import DataFetcher
from ui.dashboard import TradingDashboard
from config.settings import LOG_LEVEL, LOG_FILE


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function"""
    logger.info("="*60)
    logger.info("Best Trade Bot Starting")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    try:
        portfolio = Portfolio()
        trading_engine = TradingEngine(portfolio)
        data_fetcher = DataFetcher()
        
        logger.info("Components initialized successfully")
        
        dashboard = TradingDashboard(trading_engine)
        
        logger.info("Starting web dashboard...")
        logger.info("Open browser and navigate to http://localhost:5000")
        
        dashboard.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
