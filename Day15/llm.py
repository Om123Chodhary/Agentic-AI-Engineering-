from openai import OpenAI
import time
from logger import logger
from config import (
    BASE_URL,
    API_KEY,
    MODEL,
    MAX_RETRIES,
    TIMEOUT
)
client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY,
    timeout=TIMEOUT
)

def call_llm(messages):
    for attempt in range(1,MAX_RETRIES +1):
        try:
            logger.info(f"LLM request attempt {attempt}") 
            response = (client.chat.completions.create(
                model=MODEL,
                messages=messages
            ))
            logger.info("LLM call successful.")
            return(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            if attempt == MAX_RETRIES:
                logger.error("Maximum retry limit reached") 
                raise RuntimeError(
                    "LLM request failed after"
                    f"{MAX_RETRIES} attempts."
                ) from e          
        
        wait_time = attempt*2
        logger.info(f"Retrying in {wait_time} seconds")

        time.sleep(wait_time)