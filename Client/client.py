import socketserver, threading, webbrowser, hashlib, requests
from typing import Optional, Union
from .config import BASE_URL, LOGIN_URL, REDIRECT_PORT, LOGIN_TIMEOUT, APP_KEY, API_SECRET
from .redirect_handler import RedirectHandler
from .utils import is_port_available, force_close_port, close_previous_login

class AliceBlue:
    def __init__(self, app_key: str, api_secret: str):
        self.app_key = app_key
        self.api_secret = api_secret
        self.user_id = None
        self.auth_code = None
        self.user_session = None
        self.headers = None
        self.login_timeout = LOGIN_TIMEOUT
        self.current_server = None
        self.server_thread = None

    def login_and_get_auth_code(self):
        close_previous_login(self.current_server)
        if not is_port_available(REDIRECT_PORT):
            print("Port 8080 is busy, forcing closure...")
            force_close_port(REDIRECT_PORT)

        RedirectHandler.login_received.clear()
        RedirectHandler.auth_code = None
        RedirectHandler.user_id = None

        try:
            self.current_server = socketserver.TCPServer(("localhost", REDIRECT_PORT), RedirectHandler, bind_and_activate=False)
            self.current_server.allow_reuse_address = True
            self.current_server.server_bind()
            self.current_server.server_activate()
            RedirectHandler.current_server = self.current_server

            self.server_thread = threading.Thread(target=self.current_server.serve_forever, daemon=True)
            self.server_thread.start()

            login_url = f"{LOGIN_URL}{self.app_key}"
            print(f"Opening browser for login: {login_url}")
            webbrowser.open(login_url)

            print(f"Waiting for login (timeout: {self.login_timeout} seconds)...")
            login_success = RedirectHandler.login_received.wait(timeout=self.login_timeout)

            if not login_success:
                close_previous_login(self.current_server)
                raise TimeoutError("Login timeout: No login received")

            self.auth_code = RedirectHandler.auth_code
            self.user_id = RedirectHandler.user_id

            if not self.auth_code or not self.user_id:
                close_previous_login(self.current_server)
                raise ValueError("Login failed: Missing authCode or userId")

            print(f"Auth Code received, User ID: {self.user_id}")
            close_previous_login(self.current_server)

        except Exception as e:
            close_previous_login(self.current_server)
            raise e

    def authenticate(self):
        if not self.auth_code or not self.user_id:
            self.login_and_get_auth_code()

        raw_string = f"{self.user_id}{self.auth_code}{self.api_secret}"
        checksum = hashlib.sha256(raw_string.encode()).hexdigest()
        url = f"{BASE_URL}/open-api/od/v1/vendor/getUserDetails"
        payload = {"checkSum": checksum}
        res = requests.post(url, json=payload)

        if res.status_code != 200:
            raise Exception(f"API Error: {res.text}")

        data = res.json()
        if data.get("stat") == "Ok":
            self.user_session = data["userSession"]
            self.headers = {"Authorization": f"Bearer {self.user_session}"}
            print("Authentication Successful")
        else:
            raise Exception(f"Authentication failed: {data}")

    def get_session(self):
        return self.user_session

    def close(self):
        """Cleanup method to close any ongoing login attempts"""
        self.close_previous_login()
    

    def get_profile(self):
        url = f"{BASE_URL}/open-api/od/v1/profile"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Profile Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_holdings(self):
        url = f"{BASE_URL}/open-api/od/v1/holdings/CNC"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Holding Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_positions(self):
        url = f"{BASE_URL}/open-api/od/v1/positions"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Position Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_positions_sqroff(self, exch, symbol, qty, product, transaction_type):
        url = f"{BASE_URL}/open-api/od/v1/orders/positions/sqroff"
        payload = {
            "exch": exch,
            "symbol": symbol,
            "qty": qty,
            "product": product,
            "transaction_type": transaction_type
        }
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"Position Square Off Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")

    def get_position_conversion(self, exchange, validity, prevProduct, product, quantity, tradingSymbol, transactionType,orderSource):
        url = f"{BASE_URL}/open-api/od/v1/conversion"
        payload = {
            "exchange": exchange,
            "validity": validity,
            "prevProduct": prevProduct,
            "product": product,
            "quantity": quantity,
            "tradingSymbol": tradingSymbol,
            "transactionType": transactionType,
            "orderSource":orderSource
        }
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"Position Conversion Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_place_order(self,instrument_id: str, exchange: str, transaction_type: str, quantity: int, order_type: str, product: str,
                    order_complexity: str, price: float, validity: str, sl_leg_price: Optional[float] = None,
                    target_leg_price: Optional[float] = None, sl_trigger_price: Optional[float] = None, trailing_sl_amount: Optional[float] = None,
                    disclosed_quantity: int = 0,source: str = "API"):
        """Place an order with Alice Blue API."""

        url = f"{BASE_URL}/open-api/od/v1/orders/placeorder"

        payload = [{
            "instrumentId": instrument_id,
            "exchange": exchange,
            "transactionType": transaction_type.upper(),
            "quantity": quantity,
            "orderType": order_type.upper(),
            "product": product.upper(),
            "orderComplexity": order_complexity.upper(),
            "price": price,
            "validity": validity.upper(),
            "disclosedQuantity": disclosed_quantity,
            "source": source.upper()
        }]

        if sl_leg_price is not None:
            payload[0]["slLegPrice"] = sl_leg_price
        if target_leg_price is not None:
            payload[0]["targetLegPrice"] = target_leg_price
        if sl_trigger_price is not None:
            payload[0]["slTriggerPrice"] = sl_trigger_price
        if trailing_sl_amount is not None:
            payload[0]["trailingSlAmount"] = trailing_sl_amount

        res = requests.post(url, headers=self.headers, json=payload)

        if res.status_code != 200:
            raise Exception(f"Order Place Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_order_book(self):
        url = f"{BASE_URL}/open-api/od/v1/orders/book"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Order Book Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_order_history(self, brokerOrderId: str):
        url = f"{BASE_URL}/open-api/od/v1/orders/history"
        payload = {"brokerOrderId": brokerOrderId}
        res = requests.post(url, headers=self.headers, json = payload)
        
        if res.status_code != 200:
            raise Exception(f"Order History Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_modify_order(self, brokerOrderId:str, validity: str , quantity: Optional[int] = None,price: Optional[Union[int, float]] = None, 
                         triggerPrice: Optional[float] = None
                         ):
        url = f"{BASE_URL}/open-api/od/v1/orders/modify"
        payload = [{
            "brokerOrderId": brokerOrderId,
            "quantity": quantity if quantity else "",
            "price": price if price else "",
            "triggerPrice": triggerPrice if triggerPrice else "",
            "validity": validity.upper()
        }]
        res = requests.post(url, headers=self.headers, json=payload)
        if res.status_code != 200:
            raise Exception(f"Order Modify Error {res.status_code}: {res.text}")

        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_cancel_order(self, brokerOrderId):
        """Cancel an order."""
        url = f"{BASE_URL}/open-api/od/v1/orders/cancel"
        payload = {"brokerOrderId":brokerOrderId}
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"Order Cancel Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_trade_book(self):
        url = f"{BASE_URL}/open-api/od/v1/orders/trades"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Order Cancel Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_order_margin(self, exchange:str, instrumentId:str, transactionType:str, quantity:int, product:str, 
                         orderComplexity:str, orderType:str, validity:str, price=0.0, slTriggerPrice: Optional[Union[int, float]] = None):
        url = f"{BASE_URL}/open-api/od/v1/orders/checkMargin"
        payload = [{
            "exchange": exchange.upper(),
            "instrumentId": instrumentId.upper(),
            "transactionType": transactionType.upper(),
            "quantity": quantity,
            "product": product.upper(),
            "orderComplexity": orderComplexity.upper(),
            "orderType": orderType.upper(),
            "price": price,
            "validity": validity.upper(),
            "slTriggerPrice": slTriggerPrice if slTriggerPrice is not None else ""
        }]
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"Order Cancel Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_exit_bracket_order(self, brokerOrderId: str, orderComplexity: str):
        url = f"{BASE_URL}/open-api/od/v1/orders/exit/sno"
        payload = [{
            "brokerOrderId": brokerOrderId,
            "orderComplexity": orderComplexity.upper()
        }]
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"Exit Bracket Order Error {res.status_code}: {res.text}")
        
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_place_gtt_order(self, tradingSymbol: str, exchange: str, transactionType: str, orderType: str,
                            product: str, validity: str, quantity: int, price: float, orderComplexity: str, 
                            instrumentId: str, gttType: str, gttValue: float):
        
        url = f"{BASE_URL}/open-api/od/v1/orders/gtt/execute"
        
        payload = {
            "tradingSymbol": tradingSymbol.upper(),
            "exchange": exchange.upper(),
            "transactionType": transactionType.upper(),
            "orderType": orderType.upper(),
            "product": product.upper(),
            "validity": validity.upper(),
            "quantity": quantity, 
            "price": price, 
            "orderComplexity": orderComplexity.upper(),
            "instrumentId": instrumentId,
            "gttType": gttType.upper(),
            "gttValue": gttValue 
        }
        try:
            res = requests.post(url, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = res.json()
                error_msg = error_data.get("message") or error_data.get("emsg") or res.text
            except:
                error_msg = res.text
            raise Exception(f"GTT Order Place Error {res.status_code}: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_gtt_order_book(self):
        url = f"{BASE_URL}/open-api/od/v1/orders/gtt/orderbook"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"GTT Order Book Error {res.status_code}: {res.text}")
        
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_modify_gtt_order(self, brokerOrderId: str, instrumentId: str, tradingSymbol: str, 
                            exchange: str, orderType: str, product: str, validity: str, 
                            quantity: int, price: float, orderComplexity: str, 
                            gttType: str, gttValue: float):
        
        url = f"{BASE_URL}/open-api/od/v1/orders/gtt/modify"
        
        payload = {
            "brokerOrderId": brokerOrderId,
            "instrumentId": instrumentId,
            "tradingSymbol": tradingSymbol.upper(),
            "exchange": exchange.upper(),
            "orderType": orderType.upper(),
            "product": product.upper(),
            "validity": validity.upper(),
            "quantity": quantity,
            "price": price,
            "orderComplexity": orderComplexity.upper(),
            "gttType": gttType.upper(),
            "gttValue": gttValue
        }
        
        try:
            res = requests.post(url, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()
            
        except requests.exceptions.HTTPError as e:
            try:
                error_data = res.json()
                error_msg = error_data.get("message") or error_data.get("emsg") or res.text
            except:
                error_msg = res.text
            raise Exception(f"GTT Modify Order Error {res.status_code}: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_cancel_gtt_order(self, brokerOrderId):
        url = f"{BASE_URL}/open-api/od/v1/orders/gtt/cancel"
        payload = {"brokerOrderId": brokerOrderId}
        res = requests.post(url, headers=self.headers, json=payload)
        
        if res.status_code != 200:
            raise Exception(f"GTT Cancel Order Error {res.status_code}: {res.text}")
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
    
    def get_limits(self):
        url = f"{BASE_URL}/open-api/od/v1/limits"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code != 200:
            raise Exception(f"Exit Bracket Order Error {res.status_code}: {res.text}")   
        try:
            return res.json()
        except Exception:
            raise Exception(f"Non-JSON response: {res.text}")
