import logging
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class RiskMetrics:
    max_position_size: float
    optimal_leverage: float
    portfolio_var: float
    correlation_risk: float
    max_drawdown: float
    sharpe_ratio: float
    kelly_fraction: float


class EnhancedRiskManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_portfolio_risk = 0.012  # Further reduced to 1.2%
        self.max_position_risk = 0.006  # Further reduced to 0.6%
        self.max_correlation = 0.5  # Further reduced correlation threshold
        self.min_sharpe = 2.0  # Increased minimum Sharpe ratio
        self.risk_free_rate = 0.025  # Updated risk-free rate
        self.max_drawdown_limit = 0.15  # Maximum drawdown limit 15%
        self.positions = {}  # Current positions
        self.correlation_matrix = pd.DataFrame()  # Asset correlations

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        account_balance: float,
        historical_data: pd.DataFrame,
    ) -> float:
        """Calculate optimal position size using multiple risk metrics"""
        try:
            # 1. Calculate volatility-adjusted position size
            atr = self._calculate_atr(historical_data)
            volatility = historical_data["close"].pct_change().std()

            # Risk per trade based on ATR
            risk_amount = account_balance * self.max_position_risk

            # Avoid division by zero
            if atr[-1] > 0:
                atr_based_size = risk_amount / (atr[-1] * entry_price)
            else:
                atr_based_size = account_balance * 0.01  # Default to 1% of account

            # 2. Kelly Criterion position sizing
            returns = historical_data["close"].pct_change().dropna()
            kelly_fraction = self._calculate_kelly_fraction(returns)
            kelly_size = account_balance * kelly_fraction

            # 3. Volatility-based position sizing
            if volatility > 0:
                vol_adjusted_size = risk_amount / (volatility * entry_price)
            else:
                vol_adjusted_size = account_balance * 0.01

            # 4. Stop-loss based sizing
            sl_distance = abs(entry_price - stop_loss) / entry_price
            if sl_distance > 0:
                sl_based_size = risk_amount / (sl_distance * entry_price)
            else:
                sl_based_size = account_balance * 0.01

            # Combine different sizing methods with weights
            position_size = min(
                atr_based_size * 0.3
                + kelly_size * 0.2
                + vol_adjusted_size * 0.3
                + sl_based_size * 0.2,
                account_balance * 0.1,  # Max 10% of account per position
            )

            return max(position_size, 0.0)  # Ensure non-negative position size

        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0

    def optimize_portfolio(
        self, positions: Dict[str, Dict], historical_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, float]:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        try:
            # Calculate returns for all assets
            returns_data = {}
            for symbol in positions:
                if symbol in historical_data:
                    returns_data[symbol] = historical_data[symbol]["close"].pct_change()

            if not returns_data:
                return {symbol: 1.0 / len(positions) for symbol in positions}

            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)

            # Calculate expected returns and covariance matrix
            exp_returns = returns_df.mean()
            cov_matrix = returns_df.cov()

            # Define optimization objective (maximize Sharpe Ratio)
            def objective(weights):
                portfolio_return = np.sum(exp_returns * weights)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_std
                return -sharpe  # Minimize negative Sharpe ratio

            # Constraints
            n_assets = len(positions)
            constraints = [
                {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # Weights sum to 1
                {"type": "ineq", "fun": lambda x: x},  # Non-negative weights
            ]

            # Initial guess (equal weights)
            init_weights = np.array([1.0 / n_assets] * n_assets)

            # Optimize
            result = minimize(
                objective,
                init_weights,
                method="SLSQP",
                constraints=constraints,
                bounds=[(0, 0.4) for _ in range(n_assets)],  # Max 40% per asset
            )

            # Return optimized weights
            return dict(zip(positions.keys(), result.x))

        except Exception as e:
            self.logger.error(f"Error optimizing portfolio: {str(e)}")
            return {symbol: 1.0 / len(positions) for symbol in positions}

    def check_correlation_risk(
        self, symbol: str, direction: str, historical_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """Check correlation risk with existing positions"""
        try:
            if not self.positions:
                return True  # No existing positions

            # Calculate returns
            symbol_returns = historical_data[symbol]["close"].pct_change()

            # Calculate correlations with existing positions
            for pos_symbol, pos_data in self.positions.items():
                if pos_symbol in historical_data:
                    pos_returns = historical_data[pos_symbol]["close"].pct_change()
                    correlation = symbol_returns.corr(pos_returns)

                    # Check if correlation exceeds threshold
                    if abs(correlation) > self.max_correlation:
                        # If positions are in same direction and highly correlated
                        if (direction == pos_data["direction"] and correlation > 0) or (
                            direction != pos_data["direction"] and correlation < 0
                        ):
                            return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking correlation risk: {str(e)}")
            return False

    def calculate_portfolio_metrics(
        self, positions: Dict[str, Dict], historical_data: Dict[str, pd.DataFrame]
    ) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            portfolio_value = sum(
                pos["size"] * pos["entry_price"] for pos in positions.values()
            )

            if portfolio_value == 0:
                return RiskMetrics(
                    max_position_size=0,
                    optimal_leverage=0,
                    portfolio_var=0,
                    correlation_risk=0,
                    max_drawdown=0,
                    sharpe_ratio=0,
                    kelly_fraction=0,
                )

            # Calculate portfolio returns
            portfolio_returns = []
            weights = []

            for symbol, pos in positions.items():
                if symbol in historical_data:
                    returns = historical_data[symbol]["close"].pct_change()
                    weight = (pos["size"] * pos["entry_price"]) / portfolio_value
                    portfolio_returns.append(returns * weight)
                    weights.append(weight)

            if not portfolio_returns:
                return RiskMetrics(
                    max_position_size=0,
                    optimal_leverage=0,
                    portfolio_var=0,
                    correlation_risk=0,
                    max_drawdown=0,
                    sharpe_ratio=0,
                    kelly_fraction=0,
                )

            # Combine returns
            total_returns = pd.concat(portfolio_returns, axis=1).sum(axis=1)

            # Calculate metrics
            portfolio_var = total_returns.var()
            max_drawdown = self._calculate_max_drawdown(total_returns)
            sharpe = self._calculate_sharpe_ratio(total_returns)
            kelly = self._calculate_kelly_fraction(total_returns)

            # Calculate correlation risk
            correlation_risk = self._calculate_correlation_risk(
                positions, historical_data
            )

            # Calculate optimal leverage
            optimal_leverage = min(
                1.5,  # Max 1.5x leverage
                1 / portfolio_var if portfolio_var > 0 else 1.5,
            )

            # Calculate maximum safe position size
            max_position_size = (
                portfolio_value * self.max_position_risk / (1 + correlation_risk)
            )

            return RiskMetrics(
                max_position_size=max_position_size,
                optimal_leverage=optimal_leverage,
                portfolio_var=portfolio_var,
                correlation_risk=correlation_risk,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe,
                kelly_fraction=kelly,
            )

        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return RiskMetrics(
                max_position_size=0,
                optimal_leverage=0,
                portfolio_var=0,
                correlation_risk=0,
                max_drawdown=0,
                sharpe_ratio=0,
                kelly_fraction=0,
            )

    def _calculate_kelly_fraction(self, returns: pd.Series) -> float:
        """Calculate Kelly Criterion optimal fraction"""
        try:
            win_rate = len(returns[returns > 0]) / len(returns)
            avg_win = returns[returns > 0].mean()
            avg_loss = abs(returns[returns < 0].mean())

            if avg_loss == 0:
                return 0.0

            kelly = win_rate - ((1 - win_rate) / (avg_win / avg_loss))
            return max(0.0, min(kelly, 0.2))  # Cap at 20%

        except Exception as e:
            self.logger.error(f"Error calculating Kelly fraction: {str(e)}")
            return 0.0

    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns - self.risk_free_rate / 252  # Daily risk-free rate
            if excess_returns.std() == 0:
                return 0.0
            return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 0.0

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdowns = cumulative / rolling_max - 1
            return abs(drawdowns.min())

        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {str(e)}")
            return 0.0

    def _calculate_correlation_risk(
        self, positions: Dict[str, Dict], historical_data: Dict[str, pd.DataFrame]
    ) -> float:
        """Calculate portfolio correlation risk"""
        try:
            if len(positions) < 2:
                return 0.0

            returns_data = {}
            for symbol in positions:
                if symbol in historical_data:
                    returns_data[symbol] = historical_data[symbol]["close"].pct_change()

            if not returns_data:
                return 0.0

            # Calculate correlation matrix
            corr_matrix = pd.DataFrame(returns_data).corr()

            # Average absolute correlation
            corr_risk = (corr_matrix.abs().sum().sum() - len(corr_matrix)) / (
                len(corr_matrix) * (len(corr_matrix) - 1)
            )

            return corr_risk

        except Exception as e:
            self.logger.error(f"Error calculating correlation risk: {str(e)}")
            return 0.0

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = data["high"]
            low = data["low"]
            close = data["close"]

            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(window=period).mean()

        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return pd.Series(0, index=data.index)

    def update_position(
        self, symbol: str, size: float, entry_price: float, direction: str
    ) -> None:
        """Update position information"""
        self.positions[symbol] = {
            "size": size,
            "entry_price": entry_price,
            "direction": direction,
        }

    def remove_position(self, symbol: str) -> None:
        """Remove closed position"""
        if symbol in self.positions:
            del self.positions[symbol]
