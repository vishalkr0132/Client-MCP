import os
import sys
from typing import Optional, Union

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from server import mcp, get_alice_client, ensure_authenticated, close_alice_session, alice_manager

@mcp.tool()
def check_and_authenticate() -> dict:
    """Check if AliceBlue session is active and authenticate if needed."""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        
        session_id = alice.get_session()
        return {
            "status": "success",
            "authenticated": True,
            "session_id": session_id,
            "user_id": alice.user_id,
            "message": "Session is active"
        }
    except Exception as e:
        return {
            "status": "error",
            "authenticated": False,
            "message": str(e)
        }

@mcp.tool()
def initiate_login(force_refresh: bool = False) -> dict:
    """Login and create a new AliceBlue session if none exists or forced."""
    try:
        alice = get_alice_client(force_refresh=force_refresh)
        alice.authenticate()  # Authenticate only when this tool is called

        return {
            "status": "success",
            "message": "Login successful! New session created" if force_refresh else "Session active",
            "session_id": alice.get_session(),
            "user_id": alice.user_id,
            "action": "login_completed" if force_refresh else "no_login_needed"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Login failed: {e}"
        }

@mcp.tool()
def close_session() -> dict:
    """Explicitly close the current session (forces next call to re-authenticate)."""
    try:
        close_alice_session()
        return {
            "status": "success",
            "message": "Session closed. Next call will require re-authentication."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error closing session: {e}"
        }

@mcp.tool()
def get_profile() -> dict:
    """Fetches the user's profile details."""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {"status": "success", "data": alice.get_profile()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_holdings() -> dict:
    """Fetches the user's Holdings Stock"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {"status": "success", "data": alice.get_holdings()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@mcp.tool()
def get_positions()-> dict:
    """Fetches the user's Positions"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{"status": "success", "data": alice.get_positions()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_positions_sqroff(exch: str, symbol: str, qty: str, product: str, 
                         transaction_type: str)-> dict:
    """Position Square Off"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status":"success",
            "data": alice.get_positions_sqroff(
                exch=exch,
                symbol=symbol,
                qty=qty,
                product=product,
                transaction_type=transaction_type
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_position_conversion(exchange: str, validity: str, prevProduct: str, product: str, quantity: int, 
                            tradingSymbol: str, transactionType: str, orderSource: str)->dict:
    """Position conversion"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status":"success",
            "data": alice.get_position_conversion(
                exchange=exchange,
                validity=validity,
                prevProduct=prevProduct,
                product=product,
                quantity=quantity,
                tradingSymbol=tradingSymbol,
                transactionType=transactionType,
                orderSource=orderSource
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@mcp.tool()
def place_order(instrument_id: str, exchange: str, transaction_type: str, quantity: int, order_type: str, product: str,
                    order_complexity: str, price: float, validity: str) -> dict:
    """Places an order for the given stock."""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_place_order(
                instrument_id = instrument_id,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity = quantity,
                order_type = order_type,
                product = product,
                order_complexity = order_complexity,
                price=price,
                validity = validity
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_order_book()-> dict:
    """Fetches Order Book"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_order_book()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@mcp.tool()
def get_order_history(brokerOrderId: str)-> dict:
    """Fetchs Orders History"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_order_history(
                brokerOrderId=brokerOrderId
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_modify_order(brokerOrderId:str, validity: str , quantity: Optional[int] = None,
                     price: Optional[Union[int, float]] = None, triggerPrice: Optional[float] = None)-> dict:
    """Modify Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_modify_order(
                brokerOrderId = brokerOrderId,
                quantity= quantity if quantity else "",
                validity= validity,
                price= price if price else "",
                triggerPrice=triggerPrice if triggerPrice else ""
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_cancel_order(brokerOrderId: str)-> dict:
    """Cancel Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_cancel_order(
                brokerOrderId=brokerOrderId
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_trade_book()-> dict:
    """Fetches Trade Book"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_trade_book()
        }
    except Exception as e:
        return {"status": "error", "message" : str(e)}

@mcp.tool()
def get_order_margin(exchange:str, instrumentId:str, transactionType:str, quantity:int, product:str, 
                         orderComplexity:str, orderType:str, validity:str, price=0.0, 
                         slTriggerPrice: Optional[Union[int, float]] = None)-> dict:
    """Order Margin"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_order_margin(
                exchange=exchange,
                instrumentId = instrumentId,
                transactionType=transactionType,
                quantity=quantity,
                product=product,
                orderComplexity=orderComplexity,
                orderType=orderType,
                validity=validity,
                price=price,
                slTriggerPrice= slTriggerPrice if slTriggerPrice is not None else ""
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_exit_bracket_order(brokerOrderId: str, orderComplexity:str)->dict:
    """Exit Bracket Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_exit_bracket_order(
                brokerOrderId=brokerOrderId,
                orderComplexity=orderComplexity
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_place_gtt_order(tradingSymbol: str, exchange: str, transactionType: str, orderType: str,
                            product: str, validity: str, quantity: int, price: float, orderComplexity: str, 
                            instrumentId: str, gttType: str, gttValue: float)->dict:
    """Place GTT Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return {
            "status": "success",
            "data": alice.get_place_gtt_order(
                tradingSymbol=tradingSymbol,
                exchange=exchange,
                transactionType=transactionType,
                orderType=orderType,
                product=product,
                validity=validity,
                quantity=quantity,
                price=price,
                orderComplexity=orderComplexity,
                instrumentId = instrumentId,
                gttType=gttType,
                gttValue=gttValue
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_gtt_order_book():
    """Fetches GTT Order Book"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_gtt_order_book()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_modify_gtt_order(brokerOrderId: str, instrumentId: str, tradingSymbol: str, 
                            exchange: str, orderType: str, product: str, validity: str, 
                            quantity: int, price: float, orderComplexity: str, 
                            gttType: str, gttValue: float)->dict:
    """Modify GTT Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_modify_gtt_order(
                brokerOrderId=brokerOrderId,
                instrumentId = instrumentId,
                tradingSymbol=tradingSymbol,
                exchange=exchange,
                orderType=orderType,
                product=product,
                validity=validity,
                quantity=quantity,
                price=price,
                orderComplexity=orderComplexity,
                gttType=gttType,
                gttValue=gttValue,
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_cancel_gtt_order(brokerOrderId: str):
    """Cancel GTT Order"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_cancel_gtt_order(
                brokerOrderId=brokerOrderId
            )
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_limits():
    """Get Limits"""
    try:
        alice = get_alice_client()
        ensure_authenticated()
        return{
            "status": "success",
            "data": alice.get_limits()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}