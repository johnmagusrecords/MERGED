from rate_limiter import RateLimiter

@RateLimiter(max_calls=60, period=60)
async def get_account_balance(cst, x_security):
    # ...existing code...
    pass
