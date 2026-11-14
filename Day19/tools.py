from langchain_core.tools import tool
from datetime import datetime
import random
import string

# 1. Current Time Tool
@tool
def current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2. Roll Dice Tool
@tool
def roll_dice() -> int:
    """Rolls a standard 6-sided dice and returns the result."""
    return random.randint(1, 6)

# 3. Generate Password Tool
@tool
def generate_password(length: int = 12) -> str:
    """Generates a random secure password of a given length."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))