import os
import sys
from fastmcp import FastMCP
from dotenv import load_dotenv

# Setup project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from Client.client import AliceBlue
from Client.config import APP_KEY, API_SECRET

load_dotenv()

# Main MCP server instance (required for FastMCP Cloud)
server = FastMCP(
    name="New AliceBlue Portfolio Agent",
    dependencies=["python-dotenv", "requests"]
)

_alice_client = None

def get_alice_client(force_refresh: bool = False) -> AliceBlue:
    """Return a cached AliceBlue client, authenticate only once unless forced."""
    global _alice_client

    if _alice_client and not force_refresh:
        return _alice_client

    app_key = APP_KEY
    api_secret = API_SECRET

    if not app_key or not api_secret:
        raise Exception("Missing credentials. Please set ALICE_APP_KEY and ALICE_API_SECRET in .env file")

    alice = AliceBlue(app_key=app_key, api_secret=api_secret)
    alice.authenticate()
    _alice_client = alice
    return _alice_client

# Import all tools (they will auto-register with server)
try:
    sys.path.insert(0, current_dir)
    import tools
    print("✅ Tools imported successfully")
except ImportError as e:
    print(f"❌ Error importing tools: {e}")

# For local debugging only
if __name__ == "__main__":
    server.run(transport="sse", host="0.0.0.0", port=8000)
