import os
import requests
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CapitalComClient:
    def __init__(self, api_key, api_secret, identifier):
        self.identifier = identifier
        self.password = api_secret
        self.base_url = "https://demo-api-capital.backend-capital.com/api/v1"
        self.session = requests.Session()
        
        # Set up logging
        logging.info("Initializing Capital.com API client...")
        
        # Set up session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Perform initial authentication
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with the Capital.com API"""
        try:
            # Step 1: Get session token
            logging.info("Step 1: Getting session token...")
            session_response = self.session.get(f"{self.base_url}/session")
            
            if session_response.status_code != 200:
                logging.error(f"Failed to get session token: {session_response.text}")
                return
                
            # Step 2: Authenticate
            logging.info("Step 2: Authenticating...")
            auth_data = {
                "identifier": self.identifier,
                "password": self.password,
                "encryptedPassword": False
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/session",
                json=auth_data
            )
            
            logging.info(f"Auth response status: {auth_response.status_code}")
            logging.info(f"Auth response headers: {dict(auth_response.headers)}")
            logging.info(f"Auth response body: {auth_response.text}")
            
            if auth_response.status_code == 200:
                # Get security tokens
                cst = auth_response.headers.get('CST')
                security_token = auth_response.headers.get('X-SECURITY-TOKEN')
                
                if not cst or not security_token:
                    logging.error("Security tokens not found in response")
                    return
                    
                # Update session headers
                self.session.headers.update({
                    'CST': cst,
                    'X-SECURITY-TOKEN': security_token
                })
                
                # Step 3: Get account details
                logging.info("Step 3: Getting account details...")
                account_response = self.session.get(f"{self.base_url}/accounts")
                
                if account_response.status_code == 200:
                    account_data = account_response.json()
                    logging.info(f"Account data: {account_data}")
                    
                    if 'accounts' in account_data and account_data['accounts']:
                        # Find demo account if available
                        demo_account = next(
                            (acc for acc in account_data['accounts'] if acc.get('accountType') == 'CFD'),
                            account_data['accounts'][0]
                        )
                        
                        self.account_id = demo_account['accountId']
                        logging.info(f"Using account ID: {self.account_id}")
                        
                        # Step 4: Switch to demo account
                        logging.info("Step 4: Switching to demo account...")
                        switch_response = self.session.put(
                            f"{self.base_url}/session",
                            json={'accountId': self.account_id}
                        )
                        
                        if switch_response.status_code == 200:
                            logging.info("Successfully switched to demo account")
                            
                            # Update headers with account info
                            self.session.headers.update({
                                'X-CAP-API-ACCOUNT': self.account_id
                            })
                        else:
                            logging.error(f"Failed to switch account: {switch_response.text}")
                    else:
                        logging.error("No accounts found")
                else:
                    logging.error(f"Failed to get account details: {account_response.text}")
                    
                logging.info("Authentication completed")
                logging.info(f"Final headers: {dict(self.session.headers)}")
            else:
                logging.error(f"Authentication failed: {auth_response.text}")
                
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")

    def get_market_price(self, symbol):
        """Get current market price for a symbol"""
        try:
            # First get market details
            endpoint = f"{self.base_url}/markets?searchTerm={symbol}"
            logging.info(f"Getting market info from: {endpoint}")
            
            response = self.session.get(endpoint)
            logging.info(f"Market info response: {response.text}")
            
            if response.status_code == 200:
                markets_data = response.json()
                if 'markets' in markets_data and markets_data['markets']:
                    market = markets_data['markets'][0]
                    epic = market['epic']
                    
                    # Now get the current price
                    price_endpoint = f"{self.base_url}/markets/{epic}/details"
                    price_response = self.session.get(price_endpoint)
                    
                    if price_response.status_code == 200:
                        price_data = price_response.json()
                        if 'snapshot' in price_data:
                            bid = float(price_data['snapshot']['bid'])
                            offer = float(price_data['snapshot']['offer'])
                            return (bid + offer) / 2
                            
                logging.error(f"No price data found for {symbol}")
                return None
            elif response.status_code == 401:
                logging.info("Token expired, refreshing authentication...")
                self._authenticate()
                return self.get_market_price(symbol)
            else:
                logging.error(f"Failed to get market info: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting market price for {symbol}: {str(e)}")
            return None

    def place_market_order(self, symbol, direction, quantity):
        """Place a market order"""
        try:
            endpoint = f"{self.base_url}/positions"
            payload = {
                'epic': symbol,
                'direction': direction,
                'size': str(quantity),
                'orderType': 'MARKET',
                'guaranteedStop': False,
                'forceOpen': True
            }
            
            response = self.session.post(endpoint, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"Order placed successfully: {data}")
                return data
            elif response.status_code == 401:
                logging.info("Token expired, refreshing authentication...")
                self._authenticate()
                return self.place_market_order(symbol, direction, quantity)
            else:
                logging.error(f"Failed to place order: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error placing market order: {str(e)}")
            return None

    def get_positions(self):
        """Get current open positions"""
        try:
            endpoint = f"{self.base_url}/positions"
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logging.info("Token expired, refreshing authentication...")
                self._authenticate()
                return self.get_positions()
            else:
                logging.error(f"Failed to get positions: {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Error getting positions: {str(e)}")
            return []

    def close_position(self, position_id):
        """Close a specific position"""
        try:
            endpoint = f"{self.base_url}/positions/{position_id}"
            response = self.session.delete(endpoint)
            
            if response.status_code == 200:
                logging.info(f"Position {position_id} closed successfully")
                return True
            elif response.status_code == 401:
                logging.info("Token expired, refreshing authentication...")
                self._authenticate()
                return self.close_position(position_id)
            else:
                logging.error(f"Failed to close position: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error closing position: {str(e)}")
            return False
