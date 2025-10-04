import socket
import time
from .redirect_handler import RedirectHandler

def is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def force_close_port(port: int):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            if result == 0:
                s.shutdown(socket.SHUT_RDWR)
    except:
        pass
    time.sleep(0.5)

def close_previous_login(current_server):
    """Close any previous login attempt."""
    if RedirectHandler.current_server:
        try:
            RedirectHandler.current_server.shutdown()
            RedirectHandler.current_server.server_close()
            print("Previous login attempt closed")
        except Exception as e:
            print(f"Error closing previous server: {e}")
        finally:
            RedirectHandler.current_server = None
            RedirectHandler.login_received.clear()
            RedirectHandler.auth_code = None
            RedirectHandler.user_id = None

    if current_server:
        try:
            current_server.shutdown()
            current_server.server_close()
        except:
            pass
        finally:
            current_server = None
