from client import AliceBlue
from .config import APP_KEY, API_SECRET

if __name__ == "__main__":
    alice = AliceBlue(APP_KEY, API_SECRET)
    alice.authenticate()
    print("User Session:", alice.get_session())
    print("Profile:", alice.get_profile())
