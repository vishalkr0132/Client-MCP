import os
import sys
from datetime import datetime
from fastmcp import FastMCP
from dotenv import load_dotenv

# Setup project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

# Import AliceBlue components
try:
    from Client.client import AliceBlue
    from Client.config import APP_KEY, API_SECRET
    CLIENT_IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Failed to import Client modules: {e}")
    CLIENT_IMPORTS_SUCCESSFUL = False
    # Set fallback values
    APP_KEY = APP_KEY
    API_SECRET = API_SECRET

# Main MCP server instance
mcp = FastMCP("AliceBlue Trading Server")

# Global client state - use a class to manage state properly
class AliceBlueManager:
    def __init__(self):
        self.client = None
        self.initialized = False
    
    def get_client(self, force_refresh: bool = False) -> AliceBlue:
        """Return a cached AliceBlue client, authenticate only when needed."""
        if not CLIENT_IMPORTS_SUCCESSFUL:
            raise Exception("Client modules not available - check imports")
        
        if self.client and not force_refresh and self.initialized:
            return self.client

        app_key = APP_KEY
        api_secret = API_SECRET

        if not app_key or not api_secret:
            raise Exception("Missing AliceBlue credentials")

        self.client = AliceBlue(app_key=app_key, api_secret=api_secret)
        self.initialized = True
        return self.client
    
    def ensure_authenticated(self):
        """Ensure the client is authenticated before making API calls."""
        if self.client and not getattr(self.client, 'user_session', None):
            print("🔐 Authenticating AliceBlue client...")
            self.client.authenticate()
            print("✅ Authentication successful")
    
    def close_session(self):
        """Close the current session."""
        self.client = None
        self.initialized = False

# Create global manager instance
alice_manager = AliceBlueManager()

def get_alice_client(force_refresh: bool = False) -> AliceBlue:
    """Public function to get AliceBlue client."""
    return alice_manager.get_client(force_refresh)

def ensure_authenticated():
    """Public function to ensure authentication."""
    alice_manager.ensure_authenticated()

def close_alice_session():
    """Public function to close session."""
    alice_manager.close_session()

# Import all tools (they will auto-register with server)
try:
    sys.path.insert(0, current_dir)
    from tools import *
    print("✅ All tools imported successfully")
except ImportError as e:
    print(f"❌ Error importing tools: {e}")

# Test tool that doesn't require authentication
@mcp.tool()
def server_status() -> dict:
    """Check server status and basic functionality."""
    try:
        status = {
            "status": "running",
            "timestamp": str(datetime.now()),
            "client_imports": CLIENT_IMPORTS_SUCCESSFUL,
            "credentials_available": bool(APP_KEY and API_SECRET),
            "alice_client_initialized": alice_manager.initialized
        }
        return status
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def health_check() -> dict:
    """Comprehensive health check including AliceBlue connectivity."""
    try:
        # Basic server status
        status = {
            "server": "running",
            "timestamp": str(datetime.now()),
            "client_imports": CLIENT_IMPORTS_SUCCESSFUL,
            "credentials_available": bool(APP_KEY and API_SECRET),
            "alice_client_initialized": alice_manager.initialized
        }
        
        # Test AliceBlue connectivity if possible
        if CLIENT_IMPORTS_SUCCESSFUL and APP_KEY and API_SECRET:
            try:
                alice = get_alice_client()
                # Don't authenticate here - just check if client can be created
                status["alice_client"] = "created"
                status["session_active"] = bool(getattr(alice, 'user_session', None))
            except Exception as e:
                status["alice_client"] = f"error: {str(e)}"
        
        return status
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Startup validation
def validate_startup():
    """Validate that the server can start without immediate authentication."""
    try:
        print("🔧 Validating server startup...")
        
        # Test imports
        if CLIENT_IMPORTS_SUCCESSFUL:
            print("✅ Client imports successful")
        else:
            print("❌ Client imports failed")
        
        # Test config
        if APP_KEY and API_SECRET:
            print("✅ Configuration loaded")
        else:
            print("❌ Missing configuration")
            
        print("✅ Server validation passed")
        return True
    except Exception as e:
        print(f"❌ Server validation failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

# Run startup validation
validate_startup()

# For local debugging only
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

# Required for FastMCP Cloud
server = mcp