from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

__all__ = ['OPENAI_API_KEY', 'DATA_FOLDER', 'OUTPUT_FOLDER', 'RUST_FOLDER']


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise EnvironmentError('Environment variable OPENAI_API_KEY is required!')

RESOLVED_BASE_PATH = Path(os.getenv('BASE_PATH', Path(__file__).parent.parent.resolve())).resolve()
print(RESOLVED_BASE_PATH)

DATA_FOLDER = RESOLVED_BASE_PATH / 'data'
OUTPUT_FOLDER = DATA_FOLDER / 'output'
RUST_FOLDER = DATA_FOLDER / 'rust'
