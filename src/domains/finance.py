"""
Finance Domain
==============

Handles finance and trading-related tasks.
"""

from .base import DomainBase
from typing import Dict, List

class FinanceDomain(DomainBase):
    """Finance and trading domain handler"""
    
    def __init__(self):
        super().__init__('finance')
        self.knowledge_base = {
            'strategies': [
                'Technical Analysis (TA)',
                'Fundamental Analysis (FA)',
                'Quantitative Trading',
                'Algorithmic Trading',
                'Arbitrage Trading',
                'Risk Management'
            ],
            'indicators': [
                'Moving Averages (SMA, EMA)',
                'RSI (Relative Strength Index)',
                'MACD (Moving Average Convergence Divergence)',
                'Bollinger Bands',
                'Fibonacci Retracement',
                'Ichimoku Cloud'
            ],
            'risk_metrics': [
                'Sharpe Ratio',
                'Sortino Ratio',
                'Maximum Drawdown',
                'Beta',
                'Alpha',
                'VaR (Value at Risk)'
            ]
        }
    
    def get_knowledge(self, task: str) -> Dict:
        knowledge = super().get_knowledge(task)
        knowledge.update(self.knowledge_base)
        return knowledge
    
    def execute_step(self, step: str, context: Dict) -> str:
        if 'technical analysis' in step.lower():
            return self._perform_technical_analysis(context)
        elif 'trade' in step.lower():
            return self._execute_trade(context)
        elif 'risk' in step.lower():
            return self._manage_risk(context)
        else:
            return super().execute_step(step, context)
    
    def _perform_technical_analysis(self, context: Dict) -> str:
        symbol = context.get('symbol', 'BTC/USDT')
        return f"Technical Analysis for {symbol}: Bullish trend, RSI at 65, MACD crossover above signal"
    
    def _execute_trade(self, context: Dict) -> str:
        action = context.get('action', 'BUY')
        symbol = context.get('symbol', 'BTC/USDT')
        amount = context.get('amount', 0.001)
        return f"Executed {action} {amount} {symbol}"
    
    def _manage_risk(self, context: Dict) -> str:
        position = context.get('position', 1)
        if position == 1:
            return "Risk check: Stop-loss at -3%, Take-profit at +5%, Position sizing: 2% of portfolio"
        return "No active position - risk management idle"
    
    def generate_report(self, results: List[Dict], context: Dict) -> str:
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']
        return f"""
Finance/Trading Report:
=======================
Total Steps: {len(results)}
Successful: {len(successful)}
Failed: {len(failed)}
Symbol: {context.get('symbol', 'BTC/USDT')}
Status: {'✅ All successful' if not failed else '⚠️ Some steps failed'}
        """
