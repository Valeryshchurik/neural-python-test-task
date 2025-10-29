import asyncio

from langchain_openai import ChatOpenAI

from processors.async_graph_file_processor import AsyncGraphFileProcessor
from settings import DATA_FOLDER, OPENAI_API_KEY
from ui import print_process_finished_message


async def main():
    llm = ChatOpenAI(
        temperature=0,
        model_name="minimax/minimax-m2:free",
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY
    )

    processor = AsyncGraphFileProcessor(llm)
    tasks = [processor.process_file(f) for f in DATA_FOLDER.glob('*.py')]
    results = await asyncio.gather(*tasks)

    print_process_finished_message(results)

if __name__ == "__main__":
    asyncio.run(main())
