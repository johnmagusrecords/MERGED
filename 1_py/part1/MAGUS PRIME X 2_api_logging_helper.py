import json
import logging
import os
from datetime import datetime


class ApiLogHelper:
    """Helper class for detailed API logging and troubleshooting"""

    def __init__(self, log_dir="api_logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_request(self, method, url, headers, data=None, params=None):
        """Log a detailed request"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_dir}/request_{timestamp}.log"

        # Mask sensitive information in headers
        masked_headers = self._mask_sensitive_data(headers)

        # Create log content
        log_content = [
            f"API Request - {timestamp}",
            f"Method: {method}",
            f"URL: {url}",
            f"Headers: {json.dumps(masked_headers, indent=2)}",
        ]

        if params:
            log_content.append(f"Query Params: {json.dumps(params, indent=2)}")

        if data:
            # Mask passwords in data
            masked_data = self._mask_sensitive_data(data)
            log_content.append(f"Body: {json.dumps(masked_data, indent=2)}")

        # Write to file
        with open(filename, "w") as f:
            f.write("\n".join(log_content))

        return filename

    def log_response(self, response, request_info=None):
        """Log a detailed response"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_dir}/response_{timestamp}.log"

        # Create log content
        log_content = [
            f"API Response - {timestamp}",
        ]

        # Add request info if available
        if request_info:
            log_content.append(f"Request: {request_info}")

        log_content.append(f"Status Code: {response.status_code}")
        log_content.append(f"Headers: {json.dumps(dict(response.headers), indent=2)}")

        # Try to parse response as JSON
        try:
            json_response = response.json()
            log_content.append(f"Body (JSON): {json.dumps(json_response, indent=2)}")
        except:
            # If not JSON, log as text
            log_content.append(f"Body (Text): {response.text}")

        # Write to file
        with open(filename, "w") as f:
            f.write("\n".join(log_content))

        return filename

    def _mask_sensitive_data(self, data):
        """Mask sensitive information like API keys and passwords"""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if key.lower() in [
                    "password",
                    "api_key",
                    "key",
                    "secret",
                    "token",
                    "x-cap-api-key",
                ]:
                    if isinstance(value, str) and len(value) > 8:
                        masked_data[key] = value[:4] + "****" + value[-4:]
                    else:
                        masked_data[key] = "****"
                elif isinstance(value, (dict, list)):
                    masked_data[key] = self._mask_sensitive_data(value)
                else:
                    masked_data[key] = value
            return masked_data
        elif isinstance(data, list):
            return [
                (
                    self._mask_sensitive_data(item)
                    if isinstance(item, (dict, list))
                    else item
                )
                for item in data
            ]
        else:
            return data


# Create a global instance for easy import
api_logger = ApiLogHelper()


def log_api_interaction(func):
    """Decorator to log API interactions"""

    def wrapper(*args, **kwargs):
        try:
            # Log function call
            logging.debug(f"Calling API function: {func.__name__}")

            # Execute the function
            result = func(*args, **kwargs)

            # Log success
            logging.debug(f"API function {func.__name__} completed successfully")

            return result
        except Exception as e:
            # Log error with detailed information
            logging.error(f"API function {func.__name__} failed: {str(e)}")
            raise

    return wrapper


def setup_enhanced_logging():
    """Set up enhanced logging for API troubleshooting"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Set up file handler for debug logs
    debug_handler = logging.FileHandler("logs/api_debug.log")
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    debug_handler.setFormatter(debug_formatter)

    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(debug_handler)

    logging.info("Enhanced API logging initialized")
