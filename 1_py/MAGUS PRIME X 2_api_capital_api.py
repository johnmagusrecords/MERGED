"""
Capital.com API Integration Module

This module handles all interactions with the Capital.com trading API,
including authentication, market data retrieval, and trade execution.
"""

import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load API configuration from environment variables
CAPITAL_API_KEY = os.environ.get("CAPITAL_API_KEY", "")
CAPITAL_IDENTIFIER = os.environ.get("CAPITAL_IDENTIFIER", "")
CAPITAL_API_PASSWORD = os.environ.get("CAPITAL_API_PASSWORD", "")
CAPITAL_API_URL = os.environ.get("CAPITAL_API_URL", "https://api.capital.com/api/v1")

# Rate limiting
MAX_CALLS_PER_MINUTE = 60
call_timestamps = []


def throttle_api_call() -> None:
    """Throttle API calls to avoid rate limiting."""
    global call_timestamps

    now = time.time()
    # Remove timestamps older than 60 seconds
    call_timestamps = [ts for ts in call_timestamps if now - ts < 60]

    # If we're at the limit, wait until we can make another call
    if len(call_timestamps) >= MAX_CALLS_PER_MINUTE:
        wait_time = 60 - (now - call_timestamps[0]) + 0.1  # Add 0.1s margin
        if wait_time > 0:
            logging.warning(
                f"Rate limit approached. Waiting {wait_time:.2f}s before next call"
            )
            time.sleep(wait_time)

    # Add current timestamp
    call_timestamps.append(time.time())


# Market data caching and status
MARKET_CACHE = {}  # Stores fetched market data and metadata
MARKET_CACHE_TTL = 3600  # Cache lifetime in seconds (1 hour)
MARKET_STATUS_CACHE = {}  # Cache for market open/close status
MARKET_STATUS_TTL = 300  # Status cache lifetime (5 minutes)

# Authentication rate limiting
AUTH_ATTEMPTS = {}  # Tracks authentication attempts {identifier: (last_attempt, count)}
AUTH_LOCKOUT_TIME = 60  # Lockout time in seconds after too many attempts
MAX_AUTH_ATTEMPTS = 3  # Maximum auth attempts per minute


class ApiRequestConfig:
    """Configuration for API requests."""

    def __init__(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Initialize request configuration.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload for POST/PUT
            params: URL parameters for GET
        """
        self.method = method.upper()
        self.endpoint = endpoint
        self.data = data
        self.params = params

    def get_headers(self, api_key: str, cst: str, auth_token: str) -> Dict[str, str]:
        """Get request headers with authentication.

        Args:
            api_key: API key
            cst: CST token
            auth_token: Security token

        Returns:
            Dict with headers
        """
        headers = {"CST": cst, "X-SECURITY-TOKEN": auth_token, "X-CAP-API-KEY": api_key}

        # Add content type for POST/PUT requests
        if self.method in ["POST", "PUT"] and self.data:
            headers["Content-Type"] = "application/json"

        return headers


class CapitalAPI:
    """API client for Capital.com trading platform."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        identifier: Optional[str] = None,
        password: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        """Initialize the Capital.com API client.

        Args:
            api_key: API key (defaults to env var)
            identifier: Account identifier (defaults to env var)
            password: API password (defaults to env var)
            api_url: API URL (defaults to env var)

        Raises:
            ValueError: If required credentials are not provided when attempting auto-authentication
        """
        # Setup API parameters
        self.api_key = api_key or CAPITAL_API_KEY
        self.identifier = identifier or CAPITAL_IDENTIFIER
        self.password = password or CAPITAL_API_PASSWORD
        self.api_url = api_url or CAPITAL_API_URL

        # Authentication state
        self.authenticated = False
        self.auth_token = None
        self.cst = None
        self.auth_expiry = None

        # Initialize session
        self.session = requests.Session()

        # Set up retry mechanism
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Authenticate on init if credentials are available
        if self._has_required_credentials():
            self.authenticate()

    def _has_required_credentials(self) -> bool:
        """Check if all required credentials are available.

        Returns:
            bool: True if all required credentials are available
        """
        return bool(self.api_key and self.identifier and self.password)

    def _handle_api_error(
        self, error_msg: str, default_return: Any = None, log_level: str = "error"
    ) -> Any:
        """Handle API errors with consistent logging.

        Args:
            error_msg: Error message for logging
            default_return: Value to return on error
            log_level: Logging level to use

        Returns:
            The default return value
        """
        if log_level == "error":
            logging.error(error_msg)
        elif log_level == "warning":
            logging.warning(error_msg)
        else:
            logging.info(error_msg)

        return default_return

    def _execute_api_call(
        self,
        call_name: str,
        api_func: Callable[[], Tuple[bool, Any]],
        default_return: Any = None,
    ) -> Any:
        """Execute an API call with standard error handling.

        Args:
            call_name: Name of the API call for logging
            api_func: Function to execute that returns (success, response)
            default_return: Value to return on error

        Returns:
            API response on success, default_return on error
        """
        try:
            success, response = api_func()

            if success:
                return response
            else:
                error_msg = f"{call_name} failed: {response}"
                return self._handle_api_error(error_msg, default_return)

        except Exception as e:
            error_msg = f"Error in {call_name}: {e}"
            return self._handle_api_error(error_msg, default_return)

    def _has_valid_auth_tokens(self) -> bool:
        """Check if we have valid authentication tokens.

        Returns:
            bool: True if we have valid tokens
        """
        # Ensure both tokens exist and aren't empty
        if not self.authenticated:
            return False

        if not self.auth_token or not self.cst:
            logging.warning("Missing authentication tokens: token or CST is empty")
            return False

        # Check token expiry
        current_time = int(time.time())
        if self.auth_expiry and current_time >= self.auth_expiry:
            logging.info("Authentication token has expired")
            return False

        return True

    def ensure_auth(self) -> bool:
        """Ensure the API client is authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        # If we have valid tokens, return True
        if self._has_valid_auth_tokens():
            return True

        # Try to authenticate
        result = self.authenticate()
        return result is not None

    def _check_auth_rate_limit(self) -> bool:
        """Check if we should rate limit authentication attempts.

        Returns:
            bool: True if we can proceed with authentication, False if rate limited
        """
        if not self.identifier:
            return True

        current_time = int(time.time())

        if self.identifier in AUTH_ATTEMPTS:
            last_attempt, count = AUTH_ATTEMPTS[self.identifier]

            # Reset count if outside lockout period
            if current_time - last_attempt > AUTH_LOCKOUT_TIME:
                AUTH_ATTEMPTS[self.identifier] = (current_time, 1)
                return True

            # Check if we've exceeded max attempts
            if count >= MAX_AUTH_ATTEMPTS:
                logging.warning(
                    f"Authentication rate limited for {self.identifier}. Too many attempts."
                )
                return False

            # Increment attempt count
            AUTH_ATTEMPTS[self.identifier] = (last_attempt, count + 1)
        else:
            # First attempt
            AUTH_ATTEMPTS[self.identifier] = (current_time, 1)

        return True

    def _create_auth_payload(self):
        """Create the authentication payload.

        Returns:
            dict: Authentication payload
        """
        return {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False,
        }

    def _create_auth_headers(self):
        """Create headers for authentication request.

        Returns:
            dict: Authentication headers
        """
        return {"X-CAP-API-KEY": self.api_key, "Content-Type": "application/json"}

    def _process_auth_response(self, response):
        """Process authentication response.

        Args:
            response: API response

        Returns:
            Optional[Tuple[str, str, int]]: (auth_token, cst, expiry_time) or None on failure
        """
        # Check for successful response
        if response.status_code == 200:
            # Extract authentication tokens from headers
            cst = response.headers.get("CST")
            auth_token = response.headers.get("X-SECURITY-TOKEN")

            if not cst or not auth_token:
                logging.error(
                    "Authentication succeeded but tokens were not provided in response"
                )
                return None

            # Set authenticated flag
            self.authenticated = True
            logging.info("Authentication successful")

            # Calculate token expiry (typically 24 hours)
            expiry_time = int(time.time()) + 86400  # 24 hours
            return auth_token, cst, expiry_time

        elif response.status_code == 429:
            # Handle rate limiting explicitly
            logging.error("Authentication rate limited by API. Waiting before retry.")
            # Force a longer lockout for this identifier
            AUTH_ATTEMPTS[self.identifier] = (int(time.time()), MAX_AUTH_ATTEMPTS + 1)
            return None

        else:
            # Handle authentication failure
            error_data = response.text
            logging.error(f"Authentication failed: {response.status_code} {error_data}")
            return None

    def _make_auth_request(self):
        """Make the authentication API request.

        Returns:
            requests.Response: The API response
        """
        # Get authentication payload and headers
        payload = self._create_auth_payload()
        headers = self._create_auth_headers()

        # Make the authentication request
        throttle_api_call()

        return self.session.post(
            f"{self.api_url}/session", json=payload, headers=headers
        )

    def _handle_auth_error(self):
        """Handle authentication failure.

        Returns:
            None: Always returns None to indicate failure
        """
        logging.error("Authentication failed after multiple attempts")
        return None

    def _retry_auth_on_rate_limit(self, response, attempt):
        """Handle rate limiting during authentication attempts.

        Args:
            response: API response object
            attempt: Current attempt number

        Returns:
            bool: True if rate limited and should retry, False otherwise
        """
        if response.status_code == 429:
            wait_time = min(30 * (attempt + 1), 120)
            logging.warning(
                f"Authentication rate limited. Waiting {wait_time}s before retry..."
            )
            time.sleep(wait_time)
            return True
        return False

    def _handle_auth_network_error(self, error, attempt):
        """Handle network errors during authentication.

        Args:
            error: The exception that was raised
            attempt: Current attempt number

        Returns:
            None: Always returns None
        """
        logging.error(f"Network error during authentication: {error}")
        wait_time = 10 * (attempt + 1)
        logging.info(f"Waiting {wait_time}s before retry...")
        time.sleep(wait_time)
        return None

    def _process_single_auth_attempt(self, attempt):
        """Process a single authentication attempt.

        Args:
            attempt: Current attempt number

        Returns:
            Optional[Tuple[str, str, int]]: Auth result or None if failed
        """
        try:
            # Make the request
            response = self._make_auth_request()

            # Handle rate limiting
            if self._retry_auth_on_rate_limit(response, attempt):
                return None

            # Process the response
            result = self._process_auth_response(response)
            if result:
                self.auth_token, self.cst, self.auth_expiry = result
                self.authenticated = True
                return result

            # If authentication failed but not due to rate limiting, wait and retry
            wait_time = 5 * (attempt + 1)
            logging.info(f"Authentication failed. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            return None

        except (requests.RequestException, ConnectionError, TimeoutError) as e:
            return self._handle_auth_network_error(e, attempt)

    def _attempt_authentication(self):
        """Try to authenticate with retry logic.

        Returns:
            Optional[Tuple[str, str, int]]: Auth tokens and expiry time or None on failure
        """
        for attempt in range(3):
            result = self._process_single_auth_attempt(attempt)
            if result:
                return result

        return None

    def authenticate(self):
        """Authenticate with the broker API.

        Returns:
            Optional[Tuple[str, str, int]]: (auth_token, cst, expiry_time) or None on failure

        Raises:
            ValueError: If required credentials are missing
        """
        # Clear existing tokens
        self.auth_token = None
        self.cst = None
        self.authenticated = False

        # Check required credentials
        if not all([self.identifier, self.password, self.api_key]):
            raise ValueError(
                "Missing authentication credentials: identifier, password, and API key are required"
            )

        # Check rate limiting
        if not self._check_auth_rate_limit():
            return None

        try:
            logging.info("Authenticating with broker API...")

            # Attempt authentication with retry logic
            result = self._attempt_authentication()

            # Process result
            if result:
                return result

            # If all attempts failed
            return self._handle_auth_error()

        except Exception as e:
            logging.error(f"Unexpected authentication error: {e}")
            return None

    def _prepare_request(self, config: ApiRequestConfig) -> Tuple[str, dict]:
        """Prepare the request URL and headers.

        Args:
            config: API request configuration

        Returns:
            Tuple[str, dict]: (request URL, headers dictionary)
        """
        # Prepare headers with auth tokens
        if not self.auth_token or not self.cst:
            raise ValueError(
                "Authentication tokens not available - auth token or CST is missing"
            )

        headers = config.get_headers(self.api_key, self.cst, self.auth_token)

        # Prepare URL
        url = f"{self.api_url}/{config.endpoint}"

        return url, headers

    def _handle_json_parse(self, response):
        """Handle parsing of JSON response with proper error handling.

        Args:
            response: Response object from request

        Returns:
            dict: Parsed JSON data or error message dictionary
        """
        error_data = {
            "status": "error",
            "message": f"Status code: {response.status_code}",
        }

        try:
            return response.json()
        except ValueError:
            # Not JSON or invalid JSON
            if response.text:
                error_data["message"] = response.text
            return error_data

    def _handle_successful_response(self, response):
        """Process a successful API response.

        Args:
            response: Response object from successful request

        Returns:
            Tuple[bool, Any]: Success flag and response data
        """
        if response.headers.get("Content-Type", "").startswith("application/json"):
            return True, response.json()

        return True, {
            "status": "success",
            "message": "Operation completed successfully",
        }

    def _handle_response(self, response, config: ApiRequestConfig) -> Tuple[bool, Any]:
        """Handle API response and return formatted result.

        Args:
            response: Response object from request
            config: Original API request configuration

        Returns:
            Tuple[bool, Any]: (success flag, response data)
        """
        # Handle successful response
        if 200 <= response.status_code < 300:
            return self._handle_successful_response(response)

        # Parse error response
        error_data = self._handle_json_parse(response)

        # Handle expired tokens
        if response.status_code == 401:
            logging.warning("Token expired, re-authenticating...")
            self.authenticated = False
            if self.ensure_auth():
                # Retry the request once
                return self._make_api_request(config)

        return False, error_data

    def _make_api_request(self, config: ApiRequestConfig) -> Tuple[bool, Any]:
        """Make an API request with authentication handling.

        Args:
            config: ApiRequestConfig instance with request parameters

        Returns:
            Tuple[bool, Any]: (success, response_data)
        """
        # Ensure we're authenticated
        if not self.ensure_auth():
            return False, "Not authenticated"

        try:
            # Prepare the request
            url, headers = self._prepare_request(config)

            # Apply rate limiting
            throttle_api_call()

            # Make the request
            response = self.session.request(
                method=config.method,
                url=url,
                headers=headers,
                json=config.data if config.method in ["POST", "PUT"] else None,
                params=config.params,
            )

            # Process the response
            return self._handle_response(response, config)

        except Exception as e:
            error_msg = f"API request error: {str(e)}"
            logging.error(error_msg)
            return False, {"status": "error", "message": error_msg}

    def _get_api_data(
        self,
        call_name: str,
        config: ApiRequestConfig,
        data_key: str = None,
        default_value: Any = None,
    ) -> Any:
        """Helper method to fetch data from API endpoints with common pattern.

        Args:
            call_name: Name of the API call for logging
            config: ApiRequestConfig instance with request parameters
            data_key: Key to extract from response (if None, returns entire response)
            default_value: Default value if data_key not found or on error

        Returns:
            Extracted data or default value on error
        """

        def api_call():
            return self._make_api_request(config)

        result = self._execute_api_call(call_name, api_call, {})

        if data_key and result:
            return result.get(data_key, default_value)
        return result

    def _extract_trade_parameter(
        self, trade_params, key, fallback_key=None, default=None
    ):
        """Extract a parameter from either dict or object format.

        Args:
            trade_params: The parameters container (dict or object)
            key: Primary key to check
            fallback_key: Alternative key to check if primary not found
            default: Default value if neither key is found

        Returns:
            The parameter value
        """
        # Try dict access first
        value = trade_params.get(key, None)

        # If not found and fallback key provided, try that
        if value is None and fallback_key:
            value = trade_params.get(fallback_key, None)

        # If still not found, try object attribute access
        if value is None:
            value = getattr(trade_params, key, None)

        # If fallback key provided and still not found, try object attribute with fallback
        if value is None and fallback_key:
            value = getattr(trade_params, fallback_key, None)

        # Return found value or default
        return value if value is not None else default

    def _validate_trade_basics(self, symbol, direction, quantity):
        """Validate basic trade parameters.

        Args:
            symbol: Trading symbol
            direction: Trade direction
            quantity: Trade quantity

        Raises:
            ValueError: If any parameter is invalid
        """
        if not symbol:
            raise ValueError("Missing required trade parameter: symbol")

        if not direction or direction not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid direction: {direction}. Must be 'BUY' or 'SELL'")

        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}. Must be greater than 0")

    def _prepare_trade_parameters(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare trade parameters.

        Args:
            trade_params: Raw trade parameters

        Returns:
            Dict[str, Any]: Cleaned and validated parameters

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Extract parameters with proper type handling
        symbol = self._extract_trade_parameter(trade_params, "symbol")
        direction = self._extract_trade_parameter(trade_params, "direction", "action")
        quantity = float(
            self._extract_trade_parameter(trade_params, "quantity", default=1.0)
        )
        take_profit = self._extract_trade_parameter(trade_params, "take_profit")
        stop_loss = self._extract_trade_parameter(trade_params, "stop_loss")

        # Validate required parameters
        self._validate_trade_basics(symbol, direction, quantity)

        # Prepare trade request with validated parameters
        trade_request = {
            "epic": symbol,
            "direction": direction,
            "size": quantity,
            "orderType": "MARKET",
            "guaranteedStop": "false",
            "forceOpen": "true",
        }

        # Add take profit if specified
        if take_profit is not None:
            trade_request["limitDistance"] = str(abs(float(take_profit)))

        # Add stop loss if specified
        if stop_loss is not None:
            trade_request["stopDistance"] = str(abs(float(stop_loss)))

        return trade_request

    def execute_trade(self, trade_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a trade with the specified parameters.

        Args:
            trade_params: Dictionary with trade parameters
                Required: symbol, direction, quantity
                Optional: take_profit, stop_loss, guaranteed_stop, trailing_stop

        Returns:
            Optional[Dict[str, Any]]: Trade confirmation details or None on failure

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        try:
            # Clean and validate the trade parameters
            clean_params = self._prepare_trade_parameters(trade_params)

            config = ApiRequestConfig(
                method="POST", endpoint="positions", data=clean_params
            )

            def api_call():
                return self._make_api_request(config)

            result = self._execute_api_call("Trade execution", api_call)

            if result:
                logging.info(
                    f"Trade executed: {clean_params['epic']} {clean_params['direction']}"
                )

            return result
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logging.error(f"Unexpected error executing trade: {e}")
            return None

    def close_trade(self, deal_id: str) -> bool:
        """Close an active trade.

        Args:
            deal_id: ID of the trade to close

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If deal_id is empty or not a string
        """
        if not deal_id or not isinstance(deal_id, str):
            raise ValueError(f"Invalid deal_id: {deal_id}. Must be a non-empty string.")

        config = ApiRequestConfig(
            method="POST",
            endpoint=f"positions/{deal_id}",
            data={"direction": "NONE"},  # Typically this means close the position
        )

        def api_call():
            return self._make_api_request(config)

        result = self._execute_api_call("Close trade", api_call, False)
        if result:
            logging.info(f"Trade closed: {deal_id}")
            return True
        return False

    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get list of active trades.

        Returns:
            List[Dict[str, Any]]: List of active trades or empty list on error
        """
        config = ApiRequestConfig(method="GET", endpoint="positions")

        return self._get_api_data(
            call_name="Get active trades",
            config=config,
            data_key="positions",
            default_value=[],
        )

    def get_available_markets(self) -> List[Dict[str, Any]]:
        """Fetch and return list of available markets.

        Returns:
            List[Dict[str, Any]]: List of available markets or empty list on error
        """
        config = ApiRequestConfig(method="GET", endpoint="markets")

        return self._get_api_data(
            call_name="Get markets", config=config, data_key="markets", default_value=[]
        )

    def is_market_open(self, symbol: str) -> bool:
        """Check if a market is currently open for trading.

        Args:
            symbol: Market symbol to check

        Returns:
            bool: True if the market is open, False otherwise
        """
        try:
            # First check cache
            found_in_cache, is_open = self._get_market_status_from_cache(symbol)
            if found_in_cache:
                return is_open

            # Not in cache, query API
            config = ApiRequestConfig(
                method="GET", endpoint="markets", params={"searchTerm": symbol}
            )

            success, response = self._make_api_request(config)

            if success:
                markets = response.get("markets", [])
                for m in markets:
                    if self.normalize_symbol(
                        m.get("instrumentName", "")
                    ) == self.normalize_symbol(symbol):
                        is_open = m.get("marketStatus") == "TRADEABLE"
                        self._update_market_status_cache(symbol, is_open)
                        return is_open

            # If we got here, API call failed or symbol not found
            self._update_market_status_cache(symbol, False)
            return False
        except Exception as e:
            logging.error(f"Error checking market status for {symbol}: {e}")
            return False

    def _get_market_status_from_cache(self, symbol: str) -> Tuple[bool, bool]:
        """Get market open status from cache if available and not expired.

        Args:
            symbol: Trading symbol to check

        Returns:
            Tuple of (is_found, is_open) where is_found indicates if valid cache entry exists
        """
        cache_key = self.normalize_symbol(symbol)
        current_time = time.time()

        if cache_key in MARKET_STATUS_CACHE:
            data = MARKET_STATUS_CACHE[cache_key]
            if current_time - data["timestamp"] < MARKET_STATUS_TTL:
                return True, data["is_open"]

        return False, None

    def _update_market_status_cache(self, symbol: str, is_open: bool) -> None:
        """Update the market status cache for a symbol.

        Args:
            symbol: Trading symbol
            is_open: Whether the market is open
        """
        cache_key = self.normalize_symbol(symbol)
        MARKET_STATUS_CACHE[cache_key] = {"is_open": is_open, "timestamp": time.time()}

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format for consistent caching."""
        return symbol.upper().replace("/", "")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a market.

        Args:
            symbol: Market symbol to get price for

        Returns:
            float: Current price or None on error
        """
        try:
            # Ensure authentication
            self.ensure_auth()

            # API call to fetch current price
            config = ApiRequestConfig(method="GET", endpoint=f"prices/{symbol}")

            success, response = self._make_api_request(config)

            if success:
                price_data = response
                # Extract price from response (adapt based on actual API response format)
                current_price = price_data.get("offer", None)
                return current_price
            else:
                logging.error(f"Failed to get price for {symbol}: {response}")
                return None

        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {e}")
            return None

    def get_historical_prices(
        self, symbol: str, interval: str = "HOUR", count: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get historical price data for a symbol.

        Args:
            symbol: Market symbol
            interval: Candle interval (e.g., "HOUR", "DAY")
            count: Number of candles to fetch

        Returns:
            pandas.DataFrame: Historical price data or None on error
        """
        try:
            # Ensure authentication
            self.ensure_auth()

            # API call to get historical prices
            config = ApiRequestConfig(
                method="GET", endpoint=f"prices/{symbol}/{interval.lower()}/{count}"
            )

            success, response = self._make_api_request(config)

            if success:
                data = response
                # Process the response into a DataFrame
                prices = data.get("prices", [])
                if not prices:
                    return None

                # Convert API response to DataFrame (adapt based on actual API response format)
                df = pd.DataFrame(prices)
                df.rename(
                    columns={
                        "snapshotTime": "time",
                        "openPrice.ask": "open",
                        "highPrice.ask": "high",
                        "lowPrice.ask": "low",
                        "closePrice.ask": "close",
                        "lastTradedVolume": "volume",
                    },
                    inplace=True,
                )

                # Convert time to datetime
                df["time"] = pd.to_datetime(df["time"])
                df.set_index("time", inplace=True)

                return df
            else:
                logging.error(
                    f"Failed to get historical prices for {symbol}: {response}"
                )
                return None

        except Exception as e:
            logging.error(f"Error getting historical data for {symbol}: {e}")
            return None

    def get_markets(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Get available markets from the broker API.

        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (success, markets_data)
        """
        config = ApiRequestConfig(method="GET", endpoint="markets", params={})

        success, response = self._make_api_request(config)

        if success and "markets" in response:
            return True, response["markets"]

        return False, response

    def get_historical_prices(
        self, symbol: str, resolution: str = "HOUR", limit: int = 100
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get historical price data for a symbol.

        Args:
            symbol: Market symbol
            resolution: Time resolution (MINUTE, HOUR, DAY, etc.)
            limit: Number of candles to retrieve

        Returns:
            Tuple[bool, Dict[str, Any]]: (success, prices_data)
        """
        config = ApiRequestConfig(
            method="GET",
            endpoint=f"prices/{symbol}",
            params={
                "resolution": resolution,
                "limit": str(limit),
                "from": str(
                    int(time.time()) - (limit * 3600)
                ),  # Approximate time range
                "to": str(int(time.time())),
            },
        )

        return self._make_api_request(config)

    def get_current_price(self, symbol: str) -> Tuple[bool, Dict[str, Any]]:
        """Get the current price of a symbol.

        Args:
            symbol: Market symbol

        Returns:
            Tuple[bool, Dict[str, Any]]: (success, price_data)
        """
        config = ApiRequestConfig(method="GET", endpoint=f"markets/{symbol}", params={})

        return self._make_api_request(config)
