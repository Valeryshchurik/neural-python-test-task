from langchain_openai import ChatOpenAI

from settings import DATA_FOLDER, OPENAI_API_KEY
from file_processor import LlmPyFuncFileProcessor

llm = ChatOpenAI(
    temperature=0,
    model_name="minimax/minimax-m2:free",
    openai_api_base="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY
)
processor = LlmPyFuncFileProcessor(llm)

results = [processor.process_file(f) for f in DATA_FOLDER.glob('*.py')]
succeeded_files_count = sum(results)
failed_files_count = len(results) - succeeded_files_count

print(f'Files parsed. Successful: {succeeded_files_count}. Failed: {failed_files_count}')
