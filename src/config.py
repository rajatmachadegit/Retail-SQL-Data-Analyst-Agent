import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv()

# Database Configuration Parameters
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "retail_agent_assignment")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# Tiger AI Gateway Configuration Parameters
TIGER_AI_GATEWAY_URL = os.getenv("TIGER_AI_GATEWAY_URL", "https://api.ai-gateway.tigeranalytics.com")
TIGER_AI_GATEWAY_API_KEY = os.getenv("TIGER_AI_GATEWAY_API_KEY")
TIGER_AI_GATEWAY_MODEL = os.getenv("TIGER_AI_GATEWAY_MODEL")
