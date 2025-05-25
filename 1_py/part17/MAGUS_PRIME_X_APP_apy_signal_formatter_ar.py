from datetime import datetime


def format_signal_ar(signal: dict) -> str:
    """
    Arabic format for Capital.com styled signal.
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    direction = "شراء" if signal.get(
        'direction', '').upper() == "BUY" else "بيع"

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>إشارة تداول • {direction}</b>
━━━━━━━━━━━━━━━━━━━━━━━
<b>الأصل:</b> {signal.get('asset', 'غير متوفر')} ({signal.get('category', 'غير متوفر')})
<b>المنصة:</b> {signal.get('platform', 'غير متوفر')}
<b>نوع الاستراتيجية:</b> {signal.get('strategy_type', 'غير متوفر')}
<b>الإطار الزمني:</b> {signal.get('timeframe', 'غير متوفر')}
<b>مدة الاحتفاظ المقترحة:</b> {signal.get('holding', 'غير متوفر')}

<b>📍 الدخول:</b> {signal.get('entry', 'غير متوفر')}
<b>🛡️ وقف الخسارة:</b> {signal.get('stop_loss', 'غير متوفر')}
<b>🎯 الهدف 1:</b> {signal.get('tp1', 'غير متوفر')}
<b>🎯 الهدف 2:</b> {signal.get('tp2', 'غير متوفر')}
<b>🎯 الهدف 3:</b> {signal.get('tp3', 'غير متوفر')}

<b>🧠 شرح الاستراتيجية:</b>
{signal.get('strategy_insight', 'غير متوفر')}

<b>📊 التعليق:</b>
{signal.get('commentary', 'غير متوفر')}

🔗 <i>تم الإنشاء بواسطة MAGUS PRIME X — {timestamp}</i>
━━━━━━━━━━━━━━━━━━━━━━━
"""


def format_signal_mt5_ar(signal: dict) -> str:
    """
    Arabic format for MetaTrader 5-style simplified signal.
    """
    entry = signal.get('entry', 0)
    entry_zone = f"{entry + 2:.1f} - {entry:.1f}" if entry else "غير متوفر"
    tp_description = "20 نقطة - 40 نقطة - 60 نقطة - مفتوح"

    direction = "شراء" if signal.get(
        'direction', '').upper() == "BUY" else "بيع"
    platform = signal.get('platform', 'MetaTrader 5')

    return f"""
✅ {signal.get('asset', 'غير متوفر')} {direction} من منطقة {entry_zone}
🔰 وقف الخسارة: {signal.get('stop_loss', 'غير متوفر')}
🔰 أهداف الربح: {tp_description}
🎯 منصة: {platform}
📊 الاستراتيجية: {signal.get('strategy_type', 'غير متوفر')} — {signal.get('commentary', 'غير متوفر')}
━━━━━━━━━━━━━━━━━━━━━━━
"""
