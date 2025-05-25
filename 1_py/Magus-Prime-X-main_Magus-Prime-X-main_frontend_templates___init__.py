# templates/__init__.py

# Import only the functions – don't call them here!
from .templates import get_signal_message, get_recovery_message

# 🚫 DO NOT call the functions here!
# Example usage (move this to another script when needed):
# recovery_message = get_recovery_message(pair, direction, entry, stop_loss, tp1)
# print(recovery_message)
