import os
import logging
from dotenv import load_dotenv

class CredentialsManager:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Set up logging
        logging.info("Initializing CredentialsManager...")
        
        # Required credentials
        self.required_credentials = [
            'CAPITAL_IDENTIFIER',
            'CAPITAL_API_PASSWORD'
        ]
        
    def get_credentials(self):
        """Get API credentials from environment variables"""
        try:
            # Check if all required credentials are present
            missing_credentials = [
                cred for cred in self.required_credentials 
                if not os.getenv(cred)
            ]
            
            if missing_credentials:
                raise ValueError(
                    f"Missing required credentials: {', '.join(missing_credentials)}"
                )
            
            # Get credentials from environment variables
            credentials = {
                'IDENTIFIER': os.getenv('CAPITAL_IDENTIFIER'),
                'API_SECRET': os.getenv('CAPITAL_API_PASSWORD')
            }
            
            logging.info("Successfully loaded credentials")
            logging.info(f"Using identifier: {credentials['IDENTIFIER']}")
            
            return credentials
            
        except Exception as e:
            logging.error(f"Error getting credentials: {str(e)}")
            raise
