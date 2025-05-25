import datetime
import json
import logging
import os
import pickle
from dataclasses import asdict, dataclass
from typing import Dict, Optional

import gym
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gym import spaces
from sklearn.preprocessing import StandardScaler
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TradingDecision:
    symbol: str
    timestamp: datetime.datetime
    action: str  # 'buy', 'sell', 'hold'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    indicators_used: Dict[str, float]
    market_context: Dict[str, float]
    reasoning: str
    result: Optional[str] = None  # 'profit', 'loss', 'open'
    profit_loss: Optional[float] = None
    lessons_learned: Optional[str] = None


class TradingEnvironment(gym.Env):
    """Custom trading environment for reinforcement learning"""

    def __init__(self, df: pd.DataFrame, initial_balance=10000, max_steps=None):
        super(TradingEnvironment, self).__init__()

        self.df = df
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_price = 0
        self.done = False
        self.current_step = 0
        self.max_steps = max_steps or len(df)
        self.history = []

        # Action space: 0 = hold, 1 = buy, 2 = sell
        self.action_space = spaces.Discrete(3)

        # Observation space (normalized price, indicators, position)
        num_features = df.shape[1] + 1  # Features plus position
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(num_features,)
        )

        # Pre-normalize the data
        self.feature_scaler = StandardScaler()
        self.features = self.feature_scaler.fit_transform(self.df.values)

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0
        self.position_price = 0
        self.done = False
        self.current_step = 0
        self.history = []

        return self._get_observation()

    def step(self, action):
        if self.done:
            return self._get_observation(), 0, True, {}

        self.current_step += 1
        current_price = self.df.iloc[self.current_step - 1]["close"]
        next_price = (
            self.df.iloc[self.current_step]["close"]
            if self.current_step < len(self.df)
            else current_price
        )

        # Calculate reward based on action and price movement
        reward = 0

        # Hold
        if action == 0:
            if self.position == 1:  # Already long
                reward = (next_price - current_price) / current_price
            elif self.position == -1:  # Already short
                reward = (current_price - next_price) / current_price

        # Buy
        elif action == 1:
            if self.position == 0:  # No position, go long
                self.position = 1
                self.position_price = current_price
                # Small negative reward for transaction cost
                reward = -0.001
            elif self.position == -1:  # Close short position
                profit_pct = (self.position_price - current_price) / self.position_price
                self.balance *= 1 + profit_pct
                reward = profit_pct
                self.position = 0

        # Sell
        elif action == 2:
            if self.position == 0:  # No position, go short
                self.position = -1
                self.position_price = current_price
                # Small negative reward for transaction cost
                reward = -0.001
            elif self.position == 1:  # Close long position
                profit_pct = (current_price - self.position_price) / self.position_price
                self.balance *= 1 + profit_pct
                reward = profit_pct
                self.position = 0

        # Record this step
        self.history.append(
            {
                "step": self.current_step,
                "price": current_price,
                "action": ["hold", "buy", "sell"][action],
                "position": self.position,
                "balance": self.balance,
                "reward": reward,
            }
        )

        # Check if we're done
        if self.current_step >= self.max_steps - 1:
            self.done = True
            # Close any open positions
            if self.position != 0:
                final_price = self.df.iloc[-1]["close"]
                if self.position == 1:
                    profit_pct = (
                        final_price - self.position_price
                    ) / self.position_price
                else:
                    profit_pct = (
                        self.position_price - final_price
                    ) / self.position_price
                self.balance *= 1 + profit_pct

        return self._get_observation(), reward, self.done, {}

    def _get_observation(self):
        if self.current_step >= len(self.features):
            return np.zeros(self.observation_space.shape)

        # Get the current features and add position information
        features = self.features[self.current_step].copy()
        observation = np.append(features, [self.position])

        return observation

    def render(self, mode="human"):
        if mode != "human":
            return

        if not self.history:
            return

        # Plot prices and trades
        plt.figure(figsize=(12, 6))
        plt.plot(self.df["close"].values)

        buys = []
        sells = []

        for record in self.history:
            if record["action"] == "buy":
                buys.append((record["step"], self.df.iloc[record["step"]]["close"]))
            elif record["action"] == "sell":
                sells.append((record["step"], self.df.iloc[record["step"]]["close"]))

        if buys:
            x, y = zip(*buys)
            plt.scatter(x, y, marker="^", color="green", s=100)

        if sells:
            x, y = zip(*sells)
            plt.scatter(x, y, marker="v", color="red", s=100)

        plt.title(f"Trading Session (balance: ${self.balance:.2f})")
        plt.xlabel("Steps")
        plt.ylabel("Price")
        plt.show()


class TradeEvaluationCallback(BaseCallback):
    """Callback to evaluate agent performance during training"""

    def __init__(self, eval_env, verbose=0):
        super(TradeEvaluationCallback, self).__init__(verbose)
        self.eval_env = eval_env
        self.best_return = -np.inf

    def _on_step(self):
        if self.n_calls % 1000 == 0:
            # Run evaluation
            obs = self.eval_env.reset()
            done = False
            total_reward = 0

            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, done, _ = self.eval_env.step(action)
                total_reward += reward

            logger.info(
                f"Evaluation at step {self.n_calls}: Total return: {total_reward:.4f}"
            )

            # Save best model
            if total_reward > self.best_return:
                self.best_return = total_reward
                self.model.save("best_model")
                logger.info(f"New best model saved with return {total_reward:.4f}")

        return True


class AILearningSystem:
    """AI system that learns from trading decisions and their outcomes"""

    def __init__(self, model_dir="models"):
        self.logger = logging.getLogger(__name__)
        self.model_dir = model_dir
        self.decisions_history = []
        self.feature_scalers = {}
        self.rl_models = {}
        self.memory_size = 1000  # Store last 1000 decisions
        self.success_threshold = 0.6  # 60% success rate for reinforcement

        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)

        # Initialize the decision database
        self.decision_db_path = os.path.join(model_dir, "decisions_db.json")
        if os.path.exists(self.decision_db_path):
            try:
                with open(self.decision_db_path, "r") as f:
                    self.decisions_history = json.load(f)
                    # Convert strings back to datetime objects
                    for decision in self.decisions_history:
                        decision["timestamp"] = datetime.datetime.fromisoformat(
                            decision["timestamp"]
                        )
                self.logger.info(
                    f"Loaded {len(self.decisions_history)} historical decisions"
                )
            except Exception as e:
                self.logger.error(f"Error loading decision history: {str(e)}")
                self.decisions_history = []

    def record_decision(self, decision: TradingDecision):
        """Record a trading decision for learning"""
        decision_dict = asdict(decision)
        # Convert datetime to string for JSON serialization
        decision_dict["timestamp"] = decision_dict["timestamp"].isoformat()

        self.decisions_history.append(decision_dict)

        # Limit memory size
        if len(self.decisions_history) > self.memory_size:
            self.decisions_history = self.decisions_history[-self.memory_size :]

        # Save to disk
        try:
            with open(self.decision_db_path, "w") as f:
                json.dump(self.decisions_history, f)
        except Exception as e:
            self.logger.error(f"Error saving decision history: {str(e)}")

    def record_trade_result(self, trade_id, result, profit_loss, lessons_learned=None):
        """Record the result of a trade for learning"""
        for decision in self.decisions_history:
            if decision.get("symbol") == trade_id.get("symbol") and decision.get(
                "timestamp"
            ) == trade_id.get("timestamp"):
                decision["result"] = result
                decision["profit_loss"] = profit_loss
                decision["lessons_learned"] = lessons_learned

                # Save updated history
                try:
                    with open(self.decision_db_path, "w") as f:
                        json.dump(self.decisions_history, f)
                except Exception as e:
                    self.logger.error(
                        f"Error saving updated decision history: {str(e)}"
                    )

                break

    def generate_lessons(self, symbol, decision_data, market_data):
        """Generate lessons learned from a trade result"""
        if decision_data["result"] == "profit":
            patterns = self._identify_successful_patterns(decision_data, market_data)
            return f"Successfully traded {symbol}. Reinforcing patterns: {patterns}"
        else:
            mistakes = self._identify_mistakes(decision_data, market_data)
            return f"Unsuccessful trade on {symbol}. Identified issues: {mistakes}"

    def _identify_successful_patterns(self, decision, market_data):
        """Identify successful trading patterns from a winning trade"""
        patterns = []

        # Analyze indicators
        indicators = decision["indicators_used"]

        # Check trend alignment
        if (
            "trend_direction" in decision["market_context"]
            and decision["action"] == "buy"
            and decision["market_context"]["trend_direction"] > 0
        ):
            patterns.append("Long position aligned with uptrend")

        elif (
            "trend_direction" in decision["market_context"]
            and decision["action"] == "sell"
            and decision["market_context"]["trend_direction"] < 0
        ):
            patterns.append("Short position aligned with downtrend")

        # Check RSI conditions
        if "rsi" in indicators:
            rsi = indicators["rsi"]
            if decision["action"] == "buy" and 30 <= rsi <= 40:
                patterns.append("Bought at oversold RSI conditions")
            elif decision["action"] == "sell" and 60 <= rsi <= 70:
                patterns.append("Sold at overbought RSI conditions")

        # Check volume confirmation
        if "volume" in indicators and "avg_volume" in indicators:
            if indicators["volume"] > indicators["avg_volume"] * 1.5:
                patterns.append("Strong volume confirmation")

        # If no specific patterns found
        if not patterns:
            patterns.append("Positive risk-reward ratio")

        return ", ".join(patterns)

    def _identify_mistakes(self, decision, market_data):
        """Identify mistakes from losing trades"""
        mistakes = []

        # Analyze indicators
        indicators = decision["indicators_used"]

        # Check trend alignment
        if (
            "trend_direction" in decision["market_context"]
            and decision["action"] == "buy"
            and decision["market_context"]["trend_direction"] < 0
        ):
            mistakes.append("Long position against downtrend")

        elif (
            "trend_direction" in decision["market_context"]
            and decision["action"] == "sell"
            and decision["market_context"]["trend_direction"] > 0
        ):
            mistakes.append("Short position against uptrend")

        # Check RSI extremes
        if "rsi" in indicators:
            rsi = indicators["rsi"]
            if decision["action"] == "buy" and rsi > 70:
                mistakes.append("Bought at overbought conditions")
            elif decision["action"] == "sell" and rsi < 30:
                mistakes.append("Sold at oversold conditions")

        # Check entry timing
        if abs(decision["entry_price"] - decision["stop_loss"]) > abs(
            decision["take_profit"] - decision["entry_price"]
        ):
            mistakes.append("Poor risk-reward ratio")

        # Check time of day
        hour = decision["timestamp"].hour
        if hour in [12, 13, 14] and "forex" in decision.get("symbol", "").lower():
            mistakes.append("Trading during low liquidity hours")

        # If no specific mistakes found
        if not mistakes:
            mistakes.append("Unexpected market volatility")

        return ", ".join(mistakes)

    def train_reinforcement_model(self, symbol, market_data):
        """Train a reinforcement learning model for a specific symbol"""
        try:
            # Prepare the environment
            env = TradingEnvironment(market_data)

            # Create a vectorized environment
            vec_env = DummyVecEnv([lambda: env])

            # Create the evaluation environment
            eval_env = DummyVecEnv([lambda: TradingEnvironment(market_data)])

            # Create the callback
            eval_callback = TradeEvaluationCallback(eval_env)

            # Initialize the model
            model = PPO("MlpPolicy", vec_env, verbose=0, learning_rate=0.0003)

            # Train the model
            model.learn(total_timesteps=50000, callback=eval_callback)

            # Save the model
            model_path = os.path.join(self.model_dir, f"{symbol.lower()}_rl_model")
            model.save(model_path)

            # Save the scaler
            scaler_path = os.path.join(
                self.model_dir, f"{symbol.lower()}_feature_scaler.pkl"
            )
            with open(scaler_path, "wb") as f:
                pickle.dump(env.feature_scaler, f)

            self.rl_models[symbol] = model
            self.feature_scalers[symbol] = env.feature_scaler

            self.logger.info(f"Successfully trained RL model for {symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Error training RL model for {symbol}: {str(e)}")
            return False

    def get_rl_recommendation(self, symbol, current_data):
        """Get trading recommendation from the RL model"""
        try:
            if symbol not in self.rl_models:
                # Try to load the model
                model_path = os.path.join(self.model_dir, f"{symbol.lower()}_rl_model")
                scaler_path = os.path.join(
                    self.model_dir, f"{symbol.lower()}_feature_scaler.pkl"
                )

                if os.path.exists(model_path + ".zip") and os.path.exists(scaler_path):
                    self.rl_models[symbol] = PPO.load(model_path)

                    with open(scaler_path, "rb") as f:
                        self.feature_scalers[symbol] = pickle.load(f)
                else:
                    return None, 0.0

            # Transform the data using the saved scaler
            scaled_data = self.feature_scalers[symbol].transform(current_data.values)

            # Add position information (assuming no position)
            observation = np.append(scaled_data[-1], [0])

            # Get model prediction
            action, _ = self.rl_models[symbol].predict(observation, deterministic=True)

            # Convert action to recommendation
            actions = ["hold", "buy", "sell"]
            confidence = 0.7  # Fixed confidence as RL doesn't provide confidence

            return actions[action], confidence

        except Exception as e:
            self.logger.error(f"Error getting RL recommendation for {symbol}: {str(e)}")
            return None, 0.0

    def analyze_historical_performance(self):
        """Analyze historical trading decisions to improve future decisions"""
        if not self.decisions_history:
            return None

        # Convert list of dicts to DataFrame for analysis
        df = pd.DataFrame(self.decisions_history)

        # Filter completed trades
        completed = df[df["result"].isin(["profit", "loss"])]

        if len(completed) < 10:  # Need at least 10 trades for meaningful analysis
            return {
                "message": "Not enough historical trades for performance analysis",
                "total_trades": len(completed),
            }

        # Overall statistics
        win_rate = len(completed[completed["result"] == "profit"]) / len(completed)
        avg_profit = completed[completed["result"] == "profit"]["profit_loss"].mean()
        avg_loss = completed[completed["result"] == "loss"]["profit_loss"].mean()

        # Analyze by symbol
        symbol_performance = {}
        for symbol, group in completed.groupby("symbol"):
            symbol_win_rate = len(group[group["result"] == "profit"]) / len(group)
            symbol_performance[symbol] = {
                "win_rate": symbol_win_rate,
                "trades": len(group),
                "avg_profit": group[group["result"] == "profit"]["profit_loss"].mean(),
                "avg_loss": group[group["result"] == "loss"]["profit_loss"].mean(),
            }

        # Analyze by time of day
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        hour_performance = {}
        for hour, group in completed.groupby("hour"):
            hour_win_rate = len(group[group["result"] == "profit"]) / len(group)
            hour_performance[hour] = {"win_rate": hour_win_rate, "trades": len(group)}

        # Find best performing indicators
        indicator_performance = {}
        for decision in self.decisions_history:
            if decision.get("result") not in ["profit", "loss"]:
                continue

            for indicator, _value in decision.get("indicators_used", {}).items():
                if indicator not in indicator_performance:
                    indicator_performance[indicator] = {"profit": 0, "loss": 0}

                result = decision["result"]
                indicator_performance[indicator][result] += 1

        # Calculate indicator win rates
        for indicator, stats in indicator_performance.items():
            total = stats["profit"] + stats["loss"]
            if total > 0:
                win_rate = stats["profit"] / total
                indicator_performance[indicator]["win_rate"] = win_rate

        return {
            "overall_win_rate": win_rate,
            "average_profit": avg_profit,
            "average_loss": avg_loss,
            "profit_factor": (
                abs(avg_profit / avg_loss) if avg_loss != 0 else float("inf")
            ),
            "total_trades": len(completed),
            "symbol_performance": symbol_performance,
            "hour_performance": hour_performance,
            "indicator_performance": indicator_performance,
        }

    def generate_trading_insights(self):
        """Generate actionable trading insights based on historical performance"""
        analysis = self.analyze_historical_performance()

        if not analysis or analysis.get("message"):
            return ["Not enough historical data for insights"]

        insights = []

        # Overall performance insight
        if analysis["overall_win_rate"] > 0.6:
            insights.append(
                f"System shows strong performance with {analysis['overall_win_rate']:.2%} win rate"
            )
        elif analysis["overall_win_rate"] < 0.4:
            insights.append(
                f"System needs improvement with only {analysis['overall_win_rate']:.2%} win rate"
            )

        # Profit factor insight
        if analysis["profit_factor"] > 2:
            insights.append(
                f" "
Excellent profit factor of {analysis['pr + "ofit_factor']:.2f}. Keep position sizing + " consistent."
            )
        elif analysis["profit_factor"] < 1:
            insights.append(
                f" "
Warning: Profit factor below 1 ({analysi + "s['profit_factor']:.2f}). Losers are big + "ger than winners."
            )

        # Best performing symbols
        best_symbols = sorted(
            [
                (s, data)
                for s, data in analysis["symbol_performance"].items()
                if data["trades"] >= 5
            ],
            key=lambda x: x[1]["win_rate"],
            reverse=True,
        )

        if best_symbols:
            top_symbol, top_data = best_symbols[0]
            insights.append(
                f" "
Best performing asset: {top_symbol} with + " {top_data['win_rate']:.2%} win rate ove + "r {top_data['trades']} trades"
            )

        # Worst performing symbols
        worst_symbols = sorted(
            [
                (s, data)
                for s, data in analysis["symbol_performance"].items()
                if data["trades"] >= 5
            ],
            key=lambda x: x[1]["win_rate"],
        )

        if worst_symbols:
            bottom_symbol, bottom_data = worst_symbols[0]
            insights.append(
                f" "
Worst performing asset: {bottom_symbol}  + "with only {bottom_data['win_rate']:.2%}  + "win rate"
            )

        # Best time to trade
        best_hours = sorted(
            [
                (h, data)
                for h, data in analysis["hour_performance"].items()
                if data["trades"] >= 5
            ],
            key=lambda x: x[1]["win_rate"],
            reverse=True,
        )

        if best_hours:
            top_hour, top_hour_data = best_hours[0]
            insights.append(
                f"Best trading hour: {top_hour}:00 with {top_hour_data['win_rate']:.2%} win rate"
            )

        # Best indicators
        best_indicators = sorted(
            [
                (i, data)
                for i, data in analysis["indicator_performance"].items()
                if data.get("profit", 0) + data.get("loss", 0) >= 10
            ],
            key=lambda x: x[1].get("win_rate", 0),
            reverse=True,
        )

        if best_indicators:
            top_indicator, top_ind_data = best_indicators[0]
            insights.append(
                f" "
Most reliable signal: {
                                               top_indicator} wi + "th {top_ind_data.get(
                                                                                         'win_rate',
                                               0):.2%} + " win rate"            )

        return insights
