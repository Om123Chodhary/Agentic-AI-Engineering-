import os 
from dotenv import load_dotenv
load_dotenv()
MODEL = os.getenv(
    "MODEL","qwen3:1.7b"
)
BASE_URL = os.getenv(
    "BASE_URL","http://localhost:11434/v1"
)

API_KEY=os.getenv(
    "API_KEY","ollama"
)

MAX_STEPS= int(os.getenv("MAX_STEPS","8"))

MAX_RETRIES = int(os.getenv("MAX_RETRIES","3"))

TIMEOUT = int(os.getenv("TIMEOUT","60"))