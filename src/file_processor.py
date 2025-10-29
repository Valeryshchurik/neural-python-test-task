from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.branch import RunnableBranch
from pydantic import BaseModel

from src.parsers import (
    license_info_parser,
    function_extractor_parser,
    function_counter_parser,
    rust_translator_parser,
    RustCodeLlmOutput,
)
from src.prompts import (
    copyright_license_template,
    function_extractor_template,
    function_counter_template,
    rust_translator_template,
)


class LlmPyFuncFileProcessor:
    def __init__(self, llm, base_path):
        self.llm = llm
        self.base_path = base_path
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

    def process_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            self.file_data = file_content
            result = self.entry_point.invoke({})

        if isinstance(result, RustCodeLlmOutput):
            filename = "rust/out.rs"
            with open("rust/out.rs", "w", encoding="utf-8") as f:
                f.write(result.code)
                print(f'File {filename} generated')

        return result

