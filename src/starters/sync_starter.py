from langchain_openai import ChatOpenAI

from settings import DATA_FOLDER, OPENAI_API_KEY
from processors.sync_chain_file_processor import SyncChainFileProcessor
from ui import print_process_finished_message


def main():
    llm = ChatOpenAI(
        temperature=0,
        model_name="minimax/minimax-m2:free",
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY
    )

    processor = SyncChainFileProcessor(llm)
    results = [processor.process_file(f) for f in DATA_FOLDER.glob('*.py')]

    print_process_finished_message(results)


if __name__ == "__main__":
    main()
