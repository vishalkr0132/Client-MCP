# In Client/config.py - Add cloud support
import os

BASE_URL = "https://a3.aliceblueonline.com"
LOGIN_URL = "https://ant.aliceblueonline.com/?appcode="

# Use environment variable for redirect in cloud, fallback to localhost for local dev
# REDIRECT_URL = os.getenv("REDIRECT_URL", "http://localhost:8080")
REDIRECT_PORT = 8080 
LOGIN_TIMEOUT = 60

APP_KEY = os.getenv("APP_KEY", "OzbVrZLlNu")
API_SECRET = os.getenv("API_SECRET", "7Y16z4GR8xEiv1hwpBLqZ4CnOyxGEhgxt60RtCThj5ngwfuHpzqNgVoeNPPVco3oWvkhhaC4LRO8K2SLjG9ABVCj3rt5M8kS1F8M")