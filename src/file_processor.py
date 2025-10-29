from pathlib import Path

from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.branch import RunnableBranch
from pydantic import BaseModel

from settings import OUTPUT_FOLDER, RUST_FOLDER
from parsers import (
    license_info_parser,
    function_extractor_parser,
    function_counter_parser,
    rust_translator_parser,
    RustCodeLlmOutput,
)
from prompts import (
    copyright_license_template,
    function_extractor_template,
    function_counter_template,
    rust_translator_template,
)
from utils import get_unique_filepath


class LlmPyFuncFileProcessor:
    def __init__(self, llm):
        OUTPUT_FOLDER.mkdir(exist_ok=True)
        RUST_FOLDER.mkdir(exist_ok=True)

        self.llm = llm
        self.file_data = None
        self.file_context_keeper = RunnableLambda(
            lambda inputs: {
                **(inputs.dict() if isinstance(inputs, BaseModel) else inputs),
                "file_data": self.file_data,
            }
        )
        self.entry_point = self._prepare_processor_entry_point()

    def _prepare_processor_entry_point(self):
        copyright_license_chain = self.file_context_keeper | copyright_license_template | self.llm | license_info_parser
        function_extractor_chain = (
            self.file_context_keeper | function_extractor_template | self.llm | function_extractor_parser
        )
        function_counter_chain = (
            self.file_context_keeper | function_counter_template | self.llm | function_counter_parser
        )
        rust_translator_chain = self.file_context_keeper | rust_translator_template | self.llm | rust_translator_parser

        functions_count_branch = RunnableBranch(
            (lambda context: context.total_func_num > 2, function_extractor_chain),
            lambda x: rust_translator_chain,
        )
        function_worker_composite = function_counter_chain | functions_count_branch

        license_branch = RunnableBranch(
            (lambda context: context.is_license_open_source, function_worker_composite),
            lambda context: function_extractor_chain,
        )

        return copyright_license_chain | license_branch

    def process_file(self, input_path: Path) -> bool:
        try:
            print(f'Parsing: {input_path}')
            file_content = input_path.read_text(encoding="utf-8")
            self.file_data = file_content
            result = self.entry_point.invoke({})

            if isinstance(result, RustCodeLlmOutput):
                output_file = get_unique_filepath(RUST_FOLDER / f"{input_path.stem}.rs")
                output_file.write_text(result.code, encoding="utf-8")
            else:
                output_file = get_unique_filepath(OUTPUT_FOLDER / f"{input_path.stem}.txt")
                output_file.write_text(str(result), encoding="utf-8")
        except Exception as e:
            print(f'An error occurred while processing file: {input_path}')  # should be logger.error actually
            print(e)
            return False

        return True
