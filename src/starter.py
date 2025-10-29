from langchain_openai import ChatOpenAI

from src.file_processor import LlmPyFuncFileProcessor

MY_BASE_KEY = ''
llm = ChatOpenAI(
    temperature=0,
    model_name="minimax/minimax-m2:free",
    openai_api_base="https://openrouter.ai/api/v1",
    api_key=MY_BASE_KEY
)
base_path = '..'
processor = LlmPyFuncFileProcessor(llm)
result = processor.process_file(f"{base_path}/data/3.py")
print('The result of processing')
print(result)
