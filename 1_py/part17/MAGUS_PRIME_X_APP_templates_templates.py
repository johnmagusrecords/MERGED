import datetime
import logging
import re

try:
    from apy.config import CONFIG as config  # Ensure the config module exists in your project
except ImportError:
    config = {"localization": {"enable_arabic": False}}  # Default fallback configuration

logger = logging.getLogger(__name__)


def escape_markdown(text, version=2):
    """
    Helper function to escape telegram markup symbols.

    Args:
        text: The text to escape.
        version: Use to specify the version of telegrams Markdown:
            1 for Markdown, 2 for MarkdownV2.
    """
    if not isinstance(text, str):
        text = str(text)

    if version == 1:
        escape_chars = r"_*`["
    else:
        escape_chars = r"_*[]()~`>#+-=|{}.!"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def escape_html(text):
    """Escape HTML special characters for Telegram HTML formatting"""
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def explain_strategy(strategy):
    """Provide simple explanation of trading strategies"""
    explanations = {
        "Breakout": "Breakout occurs when price breaks above resistance or below support with momentum.",
        "Swing": "Swing trading captures multi-hour to multi-day market swings between support/resistance.",
        "Scalping": "Scalping focuses on fast trades aiming for small profit in minutes.",
        "FVG": "FVG = Fair Value Gap. Price imbalance area based on smart money theory.",
        "News-based": "Triggered by economic reports or impactful news.",
        "Trend Following": "Following established market direction after confirmation of trend strength.",
        "Mean Reversion": "Trading the return to average price after extreme price movements.",
        "Support/Resistance": "Trading bounces off key structural levels where price has historically reversed.",
        "Range Trading": "Trading between established support and resistance levels in sideways markets.",
        "Gap Trading": "Trading the spaces or 'gaps' created when price moves sharply between sessions.",
    }
    return explanations.get(strategy, "Strategy based on price and volume behavior.")


# Direct Markdown formatting functions (for use without the SignalTemplates class)


def format_signal_message(
    pair,
    entry,
    stop,
    tp1,
    tp2,
    tp3,
    strategy,
    timeframe,
    mode,
    hold,
    commentary,
    asset_type,
    sentiment=None,
    news=None,
):
    """Format a signal message using MarkdownV2 formatting"""
    lines = [
        "🚨 *TRADING SIGNAL* 🚨",
        f"\n🔹 *Pair:* {escape_markdown(pair.upper())}",
        f"🔹 *Type:* {escape_markdown(strategy)} ({escape_markdown(explain_strategy(strategy))})",
        f"🔹 *Timeframe:* {escape_markdown(timeframe)}",
        f"🔹 *Mode:* {escape_markdown(mode)}",
        f"🔹 *Hold:* {escape_markdown(hold)}",
        f"🔹 *Asset Type:* {escape_markdown(asset_type)}",
        "🔹 *MT5-Compatible:* ✅ Yes",
        f"\n💰 *Entry:* {entry}",
        f"🛑 *Stop Loss:* {stop}",
        f"✅ *TP1:* {tp1}",
        f"✅ *TP2:* {tp2}",
        f"✅ *TP3:* {tp3}",
    ]

    if commentary:
        lines.append(f"\n💬 *Commentary:* {escape_markdown(commentary)}")

    if sentiment:
        lines.append(f"\n📊 *Sentiment:* {escape_markdown(sentiment)}")

    if news:
        lines.append("\n🗞️ *Latest News:*")
        for headline in news:
            lines.append(f"- {escape_markdown(headline)}")

    return "\n".join(lines)


def format_recap_message(data):
    """Format a recap message using MarkdownV2 formatting"""
    pair = escape_markdown(data["pair"].upper())
    tp1_hit = data.get("hit_tp1", False)
    tp2_hit = data.get("hit_tp2", False)
    tp3_hit = data.get("hit_tp3", False)
    outcome = data.get("outcome", "win")
    pips = data.get("pips", 0)
    mode = escape_markdown(data.get("mode", "SAFE_RECOVERY"))

    return f"""
📊 *{pair} Signal Result*

🟢 *Entry:* {data['entry']}
🔴 *Stop Loss:* {data['stop_loss']}
{'✅' if tp1_hit else '❌'} *TP1:* {data['tp1']}
{'✅' if tp2_hit else '❌'} *TP2:* {data['tp2']}
{'✅' if tp3_hit else '❌'} *TP3:* {data['tp3']}

*Trade Outcome:* {'✅ PROFIT' if outcome == 'win' else '❌ LOSS'}
*Total Pips Gained:* {pips}
*Mode:* #{mode}
"""


class SignalTemplates:
    """
    Provides templates for different types of trading signals with proper escaping
    for Telegram's formatting options (Markdown, HTML, etc.)
    """

    def __init__(self, format_type="HTML"):
        self.format_type = format_type
        self.enable_arabic = config.get("localization", {}).get("enable_arabic", False)

    def escape(self, text):
        """Escape text based on the current format type"""
        if self.format_type == "HTML":
            return escape_html(text)
        elif self.format_type == "MarkdownV2":
            return escape_markdown(text, version=2)
        elif self.format_type == "Markdown":
            return escape_markdown(text, version=1)
        else:
            return text

    def pre_signal_template(
        self, pair, direction, type_, timeframe, platform="Capital.com"
    ):
        """Template for pre-signal alerts before the main signal"""

        if self.format_type == "HTML":
            message = f"""
🔍 <b>SIGNAL SCANNING</b> 🔍

🔹 <b>Pair:</b> {self.escape(pair)}
🔹 <b>Direction:</b> {self.escape(direction)}
🔹 <b>Timeframe:</b> {self.escape(timeframe)}
🔹 <b>Type:</b> {self.escape(type_)}

⏳ Analyzing entry and exit points...
📈 Full signal coming soon
"""
        elif self.format_type in ["Markdown", "MarkdownV2"]:
            message = f"""
*🔍 SIGNAL SCANNING 🔍*

🔹 *Pair:* {self.escape(pair)}
🔹 *Direction:* {self.escape(direction)}
🔹 *Timeframe:* {self.escape(timeframe)}
🔹 *Type:* {self.escape(type_)}

⏳ Analyzing entry and exit points...
📈 Full signal coming soon
"""
        else:
            message = f"""
🔍 SIGNAL SCANNING 🔍

🔹 Pair: {pair}
🔹 Direction: {direction}
🔹 Timeframe: {timeframe}
🔹 Type: {type_}

⏳ Analyzing entry and exit points...
📈 Full signal coming soon
"""

        # Add Arabic version if enabled
        if self.enable_arabic and self.format_type == "HTML":
            arabic = f"""
🔍 <b>فحص الإشارة</b> 🔍

🔹 <b>الزوج:</b> {self.escape(pair)}
🔹 <b>الاتجاه:</b> {self.escape(direction)}
🔹 <b>الإطار الزمني:</b> {self.escape(timeframe)}
🔹 <b>النوع:</b> {self.escape(type_)}

⏳ تحليل نقاط الدخول والخروج...
📈 الإشارة الكاملة قادمة قريبًا
"""
            message = f"{message}\n\n{arabic}"

        return message

    def full_signal_template(
        self,
        pair,
        direction,
        entry,
        stop_loss,
        tp1,
        tp2=None,
        tp3=None,
        timeframe="1h",
        type_="Breakout",
        platform="Capital.com",
        commentary=None,
        category=None,
    ):
        """
        Template for complete trading signals with all details

        Args:
            pair: Trading pair/symbol
            direction: BUY or SELL
            entry: Entry price
            stop_loss: Stop loss level
            tp1: Take profit level 1
            tp2: Take profit level 2 (optional)
            tp3: Take profit level 3 (optional)
            timeframe: Chart timeframe
            type_: Signal type/strategy
            platform: Trading platform
            commentary: Optional commentary dict with analysis
            category: Asset category (Crypto, Forex, etc.)
        """
        # Format direction with emoji
        if direction.upper() == "BUY":
            direction_formatted = "BUY 🟢"
            arabic_direction = "شراء 🟢"
        else:
            direction_formatted = "SELL 🔴"
            arabic_direction = "بيع 🔴"

        # Prepare commentary sections if provided
        strategy_explanation = ""
        technical_insights = ""
        hold_time = ""

        if commentary:
            if "strategy_explanation" in commentary:
                strategy_explanation = commentary["strategy_explanation"]
            if "technical_insights" in commentary:
                technical_insights = commentary["technical_insights"]
            if "hold_time" in commentary:
                hold_time = commentary["hold_time"]

        # Format asset category with emoji
        category_emoji = "💰"
        if category:
            if category.lower() == "crypto":
                category_emoji = "🪙"
            elif category.lower() == "forex":
                category_emoji = "💱"
            elif category.lower() in ["stock", "index"]:
                category_emoji = "📊"
            elif category.lower() == "commodity":
                category_emoji = "🛢️"

        if self.format_type == "HTML":
            message = f"""
🚨 <b>TRADING SIGNAL</b> 🚨

🔹 <b>Pair:</b> {self.escape(pair)}
🔹 <b>Type:</b> {self.escape(type_)}
🔹 <b>Direction:</b> {self.escape(direction_formatted)}
🔹 <b>Timeframe:</b> {self.escape(timeframe)}
🔹 <b>Category:</b> {category_emoji} {self.escape(category or 'Not specified')}

💰 <b>Entry:</b> {self.escape(entry)}
🛑 <b>Stop Loss:</b> {self.escape(stop_loss)}
✅ <b>TP1:</b> {self.escape(tp1)}"""

            if tp2 is not None:
                message += f"\n✅ <b>TP2:</b> {self.escape(tp2)}"
            if tp3 is not None:
                message += f"\n✅ <b>TP3:</b> {self.escape(tp3)}"

            if hold_time:
                message += f"\n⏱ <b>{self.escape(hold_time)}</b>"

            if strategy_explanation:
                message += f"\n\n<b>Strategy:</b> {self.escape(strategy_explanation)}"

            if technical_insights:
                message += f"\n\n<b>Analysis:</b> {self.escape(technical_insights)}"

            message += f"\n\n<b>Platform:</b> {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        elif self.format_type in ["Markdown", "MarkdownV2"]:
            message = f"""
*🚨 TRADING SIGNAL 🚨*

🔹 *Pair:* {self.escape(pair)}
🔹 *Type:* {self.escape(type_)}
🔹 *Direction:* {self.escape(direction_formatted)}
🔹 *Timeframe:* {self.escape(timeframe)}
🔹 *Category:* {category_emoji} {self.escape(category or 'Not specified')}

💰 *Entry:* {self.escape(entry)}
🛑 *Stop Loss:* {self.escape(stop_loss)}
✅ *TP1:* {self.escape(tp1)}"""

            if tp2 is not None:
                message += f"\n✅ *TP2:* {self.escape(tp2)}"
            if tp3 is not None:
                message += f"\n✅ *TP3:* {self.escape(tp3)}"

            if hold_time:
                message += f"\n⏱ *{self.escape(hold_time)}*"

            if strategy_explanation:
                message += f"\n\n*Strategy:* {self.escape(strategy_explanation)}"

            if technical_insights:
                message += f"\n\n*Analysis:* {self.escape(technical_insights)}"

            message += f"\n\n*Platform:* {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        else:
            # Plain text format
            message = f"""
🚨 TRADING SIGNAL 🚨

🔹 Pair: {pair}
🔹 Type: {type_}
🔹 Direction: {direction_formatted}
🔹 Timeframe: {timeframe}
🔹 Category: {category_emoji} {category or 'Not specified'}

💰 Entry: {entry}
🛑 Stop Loss: {stop_loss}
✅ TP1: {tp1}"""

            if tp2 is not None:
                message += f"\n✅ TP2: {tp2}"
            if tp3 is not None:
                message += f"\n✅ TP3: {tp3}"

            if hold_time:
                message += f"\n⏱ {hold_time}"

            if strategy_explanation:
                message += f"\n\nStrategy: {strategy_explanation}"

            if technical_insights:
                message += f"\n\nAnalysis: {technical_insights}"

            message += f"\n\nPlatform: {platform}"
            message += "\n\nGenerated by MAGUS PRIME X"

        # Add Arabic version if enabled
        if self.enable_arabic and self.format_type == "HTML":
            arabic = f"""
🚨 <b>إشارة تداول</b> 🚨

🔹 <b>الزوج:</b> {self.escape(pair)}
🔹 <b>النوع:</b> {self.escape(type_)}
🔹 <b>الاتجاه:</b> {self.escape(arabic_direction)}
🔹 <b>الإطار الزمني:</b> {self.escape(timeframe)}
🔹 <b>الفئة:</b> {category_emoji} {self.escape(category or 'غير محدد')}

💰 <b>الدخول:</b> {self.escape(entry)}
🛑 <b>وقف الخسارة:</b> {self.escape(stop_loss)}
✅ <b>هدف الربح 1:</b> {self.escape(tp1)}"""

            if tp2 is not None:
                arabic += f"\n✅ <b>هدف الربح 2:</b> {self.escape(tp2)}"
            if tp3 is not None:
                arabic += f"\n✅ <b>هدف الربح 3:</b> {self.escape(tp3)}"

            arabic += f"\n\n<b>المنصة:</b> {self.escape(platform)}"
            arabic += "\n\nتم إنشاؤها بواسطة MAGUS PRIME X"

            message = f"{message}\n\n{arabic}"

        return message

    def recap_template(
        self,
        pair,
        direction,
        entry,
        stop_loss,
        tp1,
        tp2=None,
        tp3=None,
        hit_tp1=False,
        hit_tp2=False,
        hit_tp3=False,
        hit_sl=False,
        pips=0,
        platform="Capital.com",
    ):
        """
        Template for trade recap messages

        Args:
            pair: Trading pair/symbol
            direction: BUY or SELL
            entry: Entry price
            stop_loss: Stop loss level
            tp1: Take profit level 1
            tp2: Take profit level 2 (optional)
            tp3: Take profit level 3 (optional)
            hit_tp1: Whether TP1 was hit
            hit_tp2: Whether TP2 was hit
            hit_tp3: Whether TP3 was hit
            hit_sl: Whether SL was hit
            pips: Pips/points gained or lost
            platform: Trading platform
        """
        # Determine outcome
        if hit_sl:
            outcome = "LOSS ❌"
            arabic_outcome = "خسارة ❌"
            overall_result = "🔴"
        elif hit_tp1 or hit_tp2 or hit_tp3:
            outcome = "WIN ✅"
            arabic_outcome = "ربح ✅"
            overall_result = "🟢"
        else:
            outcome = "CLOSED"
            arabic_outcome = "مغلق"
            overall_result = "⚪"

        # Format direction
        if direction.upper() == "BUY":
            direction_formatted = "BUY 🟢"
            arabic_direction = "شراء 🟢"
        else:
            direction_formatted = "SELL 🔴"
            arabic_direction = "بيع 🔴"

        if self.format_type == "HTML":
            message = f"""
📊 <b>SIGNAL RECAP {overall_result}</b>

🔹 <b>Pair:</b> {self.escape(pair)}
🔹 <b>Direction:</b> {self.escape(direction_formatted)}

💰 <b>Entry:</b> {self.escape(entry)}
🛑 <b>Stop Loss:</b> {self.escape(stop_loss)}
"""
            # Add take profit levels with hit indicators
            if tp1 is not None:
                tp1_status = "✅" if hit_tp1 else "❌"
                message += f"{tp1_status} <b>TP1:</b> {self.escape(tp1)}\n"
            if tp2 is not None:
                tp2_status = "✅" if hit_tp2 else "❌"
                message += f"{tp2_status} <b>TP2:</b> {self.escape(tp2)}\n"
            if tp3 is not None:
                tp3_status = "✅" if hit_tp3 else "❌"
                message += f"{tp3_status} <b>TP3:</b> {self.escape(tp3)}\n"

            message += f"\n<b>Outcome:</b> {outcome}"
            if pips != 0:
                pips_sign = "+" if pips > 0 else ""
                message += f"\n<b>Result:</b> {pips_sign}{pips} pips"

            message += f"\n\n<b>Platform:</b> {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        elif self.format_type in ["Markdown", "MarkdownV2"]:
            message = f"""
*📊 SIGNAL RECAP {overall_result}*

🔹 *Pair:* {self.escape(pair)}
🔹 *Direction:* {self.escape(direction_formatted)}

💰 *Entry:* {self.escape(entry)}
🛑 *Stop Loss:* {self.escape(stop_loss)}
"""
            # Add take profit levels with hit indicators
            if tp1 is not None:
                tp1_status = "✅" if hit_tp1 else "❌"
                message += f"{tp1_status} *TP1:* {self.escape(tp1)}\n"
            if tp2 is not None:
                tp2_status = "✅" if hit_tp2 else "❌"
                message += f"{tp2_status} *TP2:* {self.escape(tp2)}\n"
            if tp3 is not None:
                tp3_status = "✅" if hit_tp3 else "❌"
                message += f"{tp3_status} *TP3:* {self.escape(tp3)}\n"

            message += f"\n*Outcome:* {outcome}"
            if pips != 0:
                pips_sign = "+" if pips > 0 else ""
                message += f"\n*Result:* {pips_sign}{pips} pips"

            message += f"\n\n*Platform:* {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        else:
            # Plain text format
            message = f"""
📊 SIGNAL RECAP {overall_result}

🔹 Pair: {pair}
🔹 Direction: {direction_formatted}

💰 Entry: {entry}
🛑 Stop Loss: {stop_loss}
"""
            # Add take profit levels with hit indicators
            if tp1 is not None:
                tp1_status = "✅" if hit_tp1 else "❌"
                message += f"{tp1_status} TP1: {tp1}\n"
            if tp2 is not None:
                tp2_status = "✅" if hit_tp2 else "❌"
                message += f"{tp2_status} TP2: {tp2}\n"
            if tp3 is not None:
                tp3_status = "✅" if hit_tp3 else "❌"
                message += f"{tp3_status} TP3: {tp3}\n"

            message += f"\nOutcome: {outcome}"
            if pips != 0:
                pips_sign = "+" if pips > 0 else ""
                message += f"\nResult: {pips_sign}{pips} pips"

            message += f"\n\nPlatform: {platform}"
            message += "\n\nGenerated by MAGUS PRIME X"

        # Add Arabic version if enabled
        if self.enable_arabic and self.format_type == "HTML":
            arabic = f"""
📊 <b>ملخص الإشارة {overall_result}</b>

🔹 <b>الزوج:</b> {self.escape(pair)}
🔹 <b>الاتجاه:</:</b> {self.escape(arabic_direction)}

💰 <b>الدخول:</b> {self.escape(entry)}
🛑 <b>وقف الخسارة:</b> {self.escape(stop_loss)}
"""
            # Add take profit levels with hit indicators
            if tp1 is not None:
                tp1_status = "✅" if hit_tp1 else "❌"
                arabic += f"{tp1_status} <b>هدف الربح 1:</b> {self.escape(tp1)}\n"
            if tp2 is not None:
                tp2_status = "✅" if hit_tp2 else "❌"
                arabic += f"{tp2_status} <b>هدف الربح 2:</b> {self.escape(tp2)}\n"
            if tp3 is not None:
                tp3_status = "✅" if hit_tp3 else "❌"
                arabic += f"{tp3_status} <b>هدف الربح 3:</b> {self.escape(tp3)}\n"

            arabic += f"\n<b>النتيجة:</b> {arabic_outcome}"
            if pips != 0:
                pips_sign = "+" if pips > 0 else ""
                arabic += f"\n<b>النقاط:</b> {pips_sign}{pips}"

            arabic += f"\n\n<b>المنصة:</b> {self.escape(platform)}"
            arabic += "\n\nتم إنشاؤها بواسطة MAGUS PRIME X"

            message = f"{message}\n\n{arabic}"

        return message

    def recovery_template(
        self,
        pair,
        direction,
        entry,
        stop_loss,
        tp1,
        tp2=None,
        tp3=None,
        timeframe="1h",
        type_="Recovery",
        platform="Capital.com",
    ):
        """Template for recovery signals after stop loss is hit"""

        # Add recovery indicator to signal type
        recovery_type = f"🔄 {type_} (Recovery)"

        # Format direction with emoji
        if direction.upper() == "BUY":
            direction_formatted = "BUY 🟢"
            arabic_direction = "شراء 🟢"
        else:
            direction_formatted = "SELL 🔴"
            arabic_direction = "بيع 🔴"

        if self.format_type == "HTML":
            message = f"""
🔄 <b>RECOVERY SIGNAL</b> 🔄

🔹 <b>Pair:</b> {self.escape(pair)}
🔹 <b>Type:</b> {self.escape(recovery_type)}
🔹 <b>Direction:</:</b> {self.escape(direction_formatted)}
🔹 <b>Timeframe:</b> {self.escape(timeframe)}

💰 <b>Entry:</b> {self.escape(entry)}
🛑 <b>Stop Loss:</b> {self.escape(stop_loss)}
✅ <b>TP1:</b> {self.escape(tp1)}"""

            if tp2 is not None:
                message += f"\n✅ <b>TP2:</b> {self.escape(tp2)}"
            if tp3 is not None:
                message += f"\n✅ <b>TP3:</b> {self.escape(tp3)}"

            message += f"\n\n<b>Platform:</b> {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        elif self.format_type in ["Markdown", "MarkdownV2"]:
            message = f"""
*🔄 RECOVERY SIGNAL 🔄*

🔹 *Pair:* {self.escape(pair)}
🔹 *Type:* {self.escape(recovery_type)}
🔹 *Direction:* {self.escape(direction_formatted)}
🔹 *Timeframe:* {self.escape(timeframe)}

💰 *Entry:* {self.escape(entry)}
🛑 *Stop Loss:* {self.escape(stop_loss)}
✅ *TP1:* {self.escape(tp1)}"""

            if tp2 is not None:
                message += f"\n✅ *TP2:* {self.escape(tp2)}"
            if tp3 is not None:
                message += f"\n✅ *TP3:* {self.escape(tp3)}"

            message += f"\n\n*Platform:* {self.escape(platform)}"
            message += "\n\nGenerated by MAGUS PRIME X"

        else:
            # Plain text format
            message = f"""
🔄 RECOVERY SIGNAL 🔄

🔹 Pair: {pair}
🔹 Type: {recovery_type}
🔹 Direction: {direction_formatted}
🔹 Timeframe: {timeframe}

💰 Entry: {entry}
🛑 Stop Loss: {stop_loss}
✅ TP1: {tp1}"""

            if tp2 is not None:
                message += f"\n✅ TP2: {tp2}"
            if tp3 is not None:
                message += f"\n✅ TP3: {tp3}"

            message += f"\n\nPlatform: {platform}"
            message += "\n\nGenerated by MAGUS PRIME X"

        # Add Arabic version if enabled
        if self.enable_arabic and self.format_type == "HTML":
            arabic = f"""
🔄 <b>إشارة تعافي</b> 🔄

🔹 <b>الزوج:</b> {self.escape(pair)}
🔹 <b>النوع:</b> {self.escape(recovery_type)}
🔹 <b>الاتجاه:</b> {self.escape(arabic_direction)}
🔹 <b>الإطار الزمني:</b> {self.escape(timeframe)}

💰 <b>الدخول:</b> {self.escape(entry)}
🛑 <b>وقف الخسارة:</b> {self.escape(stop_loss)}
✅ <b>هدف الربح 1:</b> {self.escape(tp1)}"""

            if tp2 is not None:
                arabic += f"\n✅ <b>هدف الربح 2:</b> {self.escape(tp2)}"
            if tp3 is not None:
                arabic += f"\n✅ <b>هدف الربح 3:</b> {self.escape(tp3)}"

            arabic += f"\n\n<b>المنصة:</b> {self.escape(platform)}"
            arabic += "\n\nتم إنشاؤها بواسطة MAGUS PRIME X"

            message = f"{message}\n\n{arabic}"

        return message

    def news_alert_template(
        self, headline, assets_affected, impact_level="High", source="News API"
    ):
        """Template for news alerts that might impact trading"""

        # Format impact level with emoji
        if impact_level.lower() == "high":
            impact_emoji = "🔴"
            arabic_impact = "عالي 🔴"
        elif impact_level.lower() == "medium":
            impact_emoji = "🟠"
            arabic_impact = "متوسط 🟠"
        else:
            impact_emoji = "🟡"
            arabic_impact = "منخفض 🟡"

        # Format assets list
        if isinstance(assets_affected, list):
            assets_str = ", ".join(assets_affected)
        else:
            assets_str = str(assets_affected)

        if self.format_type == "HTML":
            message = f"""
📰 <b>MARKET NEWS ALERT</b> 📰

📊 <b>Impact Level:</b> {impact_emoji} {self.escape(impact_level)}
🔹 <b>Assets Affected:</b> {self.escape(assets_str)}

<b>Headline:</b>
{self.escape(headline)}

<b>Source:</b> {self.escape(source)}
<b>Time:</b> {self.escape(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}

⚠️ <b>Trading Caution Advised</b> ⚠️
"""
        elif self.format_type in ["Markdown", "MarkdownV2"]:
            message = f"""
*📰 MARKET NEWS ALERT 📰*

📊 *Impact Level:* {impact_emoji} {self.escape(impact_level)}
🔹 *Assets Affected:* {self.escape(assets_str)}

*Headline:*
{self.escape(headline)}

*Source:* {self.escape(source)}
*Time:* {self.escape(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}

*⚠️ Trading Caution Advised ⚠️*
"""
        else:
            # Plain text format
            message = f"""
📰 MARKET NEWS ALERT 📰

📊 Impact Level: {impact_emoji} {impact_level}
🔹 Assets Affected: {assets_str}

Headline:
{headline}

Source: {source}
Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

⚠️ Trading Caution Advised ⚠️
"""

        # Add Arabic version if enabled
        if self.enable_arabic and self.format_type == "HTML":
            arabic = f"""
📰 <b>تنبيه أخبار السوق</b> 📰

📊 <b>مستوى التأثير:</b> {self.escape(arabic_impact)}
🔹 <b>الأصول المتأثرة:</b> {self.escape(assets_str)}

<b>العنوان:</b>
{self.escape(headline)}

<b>المصدر:</b> {self.escape(source)}
<b>الوقت:</b> {self.escape(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}

⚠️ <b>ينصح بالحذر في التداول</b> ⚠️
"""
            message = f"{message}\n\n{arabic}"

        return message


# Create a global instance for easy access
signal_templates = SignalTemplates(format_type="HTML")


def get_pre_signal_message(pair, direction, type_, timeframe, platform="Capital.com"):
    """Global function to get a pre-signal message"""
    return signal_templates.pre_signal_template(
        pair, direction, type_, timeframe, platform
    )


def get_signal_message(
    pair,
    direction,
    entry,
    stop_loss,
    tp1,
    tp2=None,
    tp3=None,
    timeframe="1h",
    type_="Breakout",
    platform="Capital.com",
    commentary=None,
    category=None,
):
    """Global function to get a full signal message"""
    return signal_templates.full_signal_template(
        pair,
        direction,
        entry,
        stop_loss,
        tp1,
        tp2,
        tp3,
        timeframe,
        type_,
        platform,
        commentary,
        category,
    )


def get_recap_message(
    pair,
    direction,
    entry,
    stop_loss,
    tp1,
    tp2=None,
    tp3=None,
    hit_tp1=False,
    hit_tp2=False,
    hit_tp3=False,
    hit_sl=False,
    pips=0,
    platform="Capital.com",
):
    """Global function to get a signal recap message"""
    return signal_templates.recap_template(
        pair,
        direction,
        entry,
        stop_loss,
        tp1,
        tp2,
        tp3,
        hit_tp1,
        hit_tp2,
        hit_tp3,
        hit_sl,
        pips,
        platform,
    )


def get_recovery_message(
    pair,
    direction,
    entry,
    stop_loss,
    tp1,
    tp2=None,
    tp3=None,
    timeframe="1h",
    type_="Recovery",
    platform="Capital.com",
):
    """Global function to get a recovery signal message"""
    return signal_templates.recovery_template(
        pair, direction, entry, stop_loss, tp1, tp2, tp3, timeframe, type_, platform
    )


def get_news_alert_message(
    headline, assets_affected, impact_level="High", source="News API"
):
    """Global function to get a news alert message"""
    return signal_templates.news_alert_template(
        headline, assets_affected, impact_level, source
    )


# === SIMPLE TEMPLATES (BACKWARD COMPATIBILITY) ===


def signal_template(data):
    """
    Simple bilingual template for trading signals (backward compatibility)

    Args:
        data: Dictionary with signal parameters

    Returns:
        str: Formatted signal message
    """
    return f"""
🚨 إشارة تداول جديدة 🚨
🔹 الزوج: {data['pair']} ({data['asset_type']})
🔹 النوع: {data['strategy']} {'شراء' if data['direction'] == 'BUY' else 'بيع'}
🔹 الإطار الزمني: {data['timeframe']}
📊 المنصة: {data['platform']}

💰 الدخول: {data['entry']}
🛑 وقف الخسارة: {data['stop_loss']}
✅ الهدف 1: {data['tp1']}
✅ الهدف 2: {data['tp2']}
✅ الهدف 3: {data['tp3']}

💬 التعليق: {data['commentary']}
🕒 التوصية: {data['hold_time']}
──────────────
🚨 NEW SIGNAL ALERT 🚨
🔹 Pair: {data['pair']} ({data['asset_type']})
🔹 Type: {data['strategy']} {data['direction']}
🔹 Timeframe: {data['timeframe']}
📊 Platform: {data['platform']}

💰 Entry: {data['entry']}
🛑 Stop Loss: {data['stop_loss']}
✅ TP1: {data['tp1']}
✅ TP2: {data['tp2']}
✅ TP3: {data['tp3']}

💬 Commentary: {data['commentary']}
🕒 Recommendation: {data['hold_time']}
""".strip()


def pre_signal_alert():
    """Simple bilingual pre-signal alert (backward compatibility)"""
    return """
🔔🚨 *تنبيه مسبق بإشارة تداول قادمة* 🚨🔔

⚡ استعدوا، يتم حالياً تحليل الأسواق لتحديد أفضل فرصة تداول.

──────────────

🔔🚨 *PRE-SIGNAL ALERT* 🚨🔔

⚡ Get ready! Market scanning in progress for the next opportunity...
""".strip()


def signal_recap(result, asset):
    """
    Simple signal recap message (backward compatibility)

    Args:
        result: Result type ('tp1', 'tp2', 'tp3', 'sl', 'closed')
        asset: Asset/pair name

    Returns:
        str: Formatted recap message
    """
    outcome = {
        "tp1": "✅ TP1 Hit",
        "tp2": "✅ TP2 Hit",
        "tp3": "✅ TP3 Hit",
        "sl": "🛑 Stop Loss Hit",
        "closed": "⚠️ Trade Closed Early",
    }

    return f"""
📊 Signal Recap for {asset}:
{outcome.get(result, '⚠️ Unknown Outcome')}

Stay tuned for next opportunity... 🔍
""".strip()


def market_closed_message(reopens_in):
    """
    Bilingual message for closed markets (backward compatibility)

    Args:
        reopens_in: Hours until market reopens

    Returns:
        str: Formatted message
    """
    return f"""
🚫 السوق مغلق حالياً

🕒 سيتم إعادة فتح السوق خلال {reopens_in} ساعة

──────────────

🚫 Market is currently closed.

🕒 Will reopen in {reopens_in} hours.
""".strip()


# Function for generating combined signal messages (new format with backward compatibility)
def generate_signal_message(
    pair,
    direction,
    entry,
    stop_loss,
    take_profits,
    asset_type=None,
    strategy=None,
    timeframe=None,
    hold_time=None,
    commentary=None,
    platform="Capital.com",
):
    """
    Generate a complete signal message with bilingual support

    Args:
        pair: Trading pair/symbol
        direction: BUY or SELL
        entry: Entry price
        stop_loss: Stop loss level
        take_profits: List of take profit prices [tp1, tp2, tp3]
        asset_type: Asset type (Crypto, Forex, etc.)
        strategy: Signal type/strategy
        timeframe: Chart timeframe
        hold_time: Expected hold time
        commentary: Commentary/analysis text
        platform: Trading platform

    Returns:
        str: Formatted signal message
    """
    # Extract take profit levels
    tp1 = take_profits[0] if take_profits and len(take_profits) > 0 else None
    tp2 = take_profits[1] if take_profits and len(take_profits) > 1 else None
    tp3 = take_profits[2] if take_profits and len(take_profits) > 2 else None

    # Use the full template function
    return get_signal_message(
        pair=pair,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        timeframe=timeframe or "1h",
        type_=strategy or "Breakout",
        platform=platform,
        commentary={"technical_insights": commentary} if commentary else None,
        category=asset_type,
    )


def generate_recap_message(
    pair, result, exit_price, notes=None, entry=None, targets_hit=None
):
    """
    Generate a recap message with bilingual support

    Args:
        pair: Trading pair/symbol
        result: Trade result ("WIN", "LOSS", etc)
        exit_price: Exit price
        notes: Additional notes (optional)
        entry: Entry price (optional)
        targets_hit: Dict with keys tp1, tp2, tp3, sl and boolean values

    Returns:
        str: Formatted recap message
    """
    # If simple format requested with no details
    if not entry and not targets_hit:
        return signal_recap(
            (
                result.lower()
                if result.lower() in ["tp1", "tp2", "tp3", "sl", "closed"]
                else "closed"
            ),
            pair,
        )

    # Get hit target information
    hit_tp1 = targets_hit.get("tp1", False) if targets_hit else False
    hit_tp2 = targets_hit.get("tp2", False) if targets_hit else False
    hit_tp3 = targets_hit.get("tp3", False) if targets_hit else False
    hit_sl = targets_hit.get("sl", False) if targets_hit else False

    # Calculate pips (placeholder - in a real implementation you'd calculate actual pips)
    pips = 0

    # Determine direction based on targets (placeholder - you'd need actual direction)
    direction = "BUY"

    # Use the comprehensive recap template
    return get_recap_message(
        pair=pair,
        direction=direction,
        entry=entry or exit_price,  # Fallback if no entry provided
        stop_loss=0,  # Placeholder
        tp1=0,  # Placeholder
        tp2=0,  # Placeholder
        tp3=0,  # Placeholder
        hit_tp1=hit_tp1,
        hit_tp2=hit_tp2,
        hit_tp3=hit_tp3,
        hit_sl=hit_sl,
        pips=pips,
    )


if __name__ == "__main__":
    # Simple test script
    print("Signal Templates Test")
    print("-" * 50)

    # Test pre-signal template
    pre_signal = get_pre_signal_message("BTCUSD", "BUY", "Breakout", "4h")
    print(pre_signal)
    print("-" * 50)

    # Test full signal template
    commentary = {
        "strategy_explanation": "This is a breakout strategy that trades the break of key levels.",
        "technical_insights": "Strong momentum with increasing volume suggests continued upward movement.",
        "hold_time": "Expected hold time: 48 hours",
    }

    full_signal = get_signal_message(
        "BTCUSD",
        "BUY",
        65000,
        64000,
        66000,
        67000,
        68000,
        "4h",
        "Breakout",
        "Capital.com",
        commentary,
        "Crypto",
    )
    print(full_signal)
    print("-" * 50)

    # Test recap template
    recap = get_recap_message(
        "BTCUSD",
        "BUY",
        65000,
        64000,
        66000,
        67000,
        68000,
        True,
        False,
        False,
        False,
        100,
    )
    print(recap)
    print("-" * 50)

    # Test recovery template
    recovery = get_recovery_message(
        "BTCUSD", "BUY", 65500, 64500, 66500, 67500, 68500, "4h", "Breakout Recovery"
    )
    print(recovery)
    print("-" * 50)

    # Test news alert template
    news_alert = get_news_alert_message(
        "Fed announces 0.25% interest rate hike, citing inflation concerns",
        ["USD", "US30", "GOLD"],
        "High",
        "Federal Reserve",
    )
    print(news_alert)
    print("-" * 50)

    # Test simple backwards-compatible functions
    print("Testing backwards-compatible functions:")

    # Test simple signal template
    simple_signal = signal_template(
        {
            "pair": "BTCUSD",
            "asset_type": "Crypto",
            "strategy": "Breakout",
            "direction": "BUY",
            "timeframe": "4h",
            "platform": "Capital.com",
            "entry": "65000",
            "stop_loss": "64000",
            "tp1": "66000",
            "tp2": "67000",
            "tp3": "68000",
            "commentary": "Strong momentum with increasing volume",
            "hold_time": "48 hours",
        }
    )
    print(simple_signal)
    print("-" * 50)

    # Test simple pre-signal alert
    simple_pre_signal = pre_signal_alert()
    print(simple_pre_signal)
    print("-" * 50)

    # Test simple recap
    simple_recap = signal_recap("tp1", "BTCUSD")
    print(simple_recap)
    print("-" * 50)

    # Test market closed message
    market_closed = market_closed_message(12)
    print(market_closed)
