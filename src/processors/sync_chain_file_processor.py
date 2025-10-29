from pathlib import Path

from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.branch import RunnableBranch
from pydantic import BaseModel

from processors.base_llm_file_processor import BaseLlmFileProcessor
from settings import OUTPUT_FOLDER, RUST_FOLDER
from parsers import RustCodeLlmOutput

from utils import get_unique_filepath, prepare_traceback_text


class SyncChainFileProcessor(BaseLlmFileProcessor):
    def __init__(self, llm):
        super().__init__(llm)
        self.file_data = None
        self.file_context_keeper = RunnableLambda(
            lambda inputs: {
                **(inputs.dict() if isinstance(inputs, BaseModel) else inputs),
                "file_data": self.file_data,
            }
        )
        self.entry_point = self._prepare_processor_entry_point()

    def _prepare_processor_entry_point(self):
        contexted_copyright_license_chain = self.file_context_keeper | self.copyright_license_chain
        contexted_function_extractor_chain = self.file_context_keeper | self.function_extractor_chain
        contexted_function_counter_chain = self.file_context_keeper | self.function_counter_chain
        contexted_rust_translator_chain = self.file_context_keeper | self.rust_translator_chain

        functions_count_branch = RunnableBranch(
            (lambda context: context.total_func_num > 2, contexted_function_extractor_chain),
            lambda x: contexted_rust_translator_chain,
        )
        function_worker_composite = contexted_function_counter_chain | functions_count_branch

        license_branch = RunnableBranch(
            (lambda context: context.is_license_open_source, function_worker_composite),
            lambda context: contexted_function_extractor_chain,
        )

        return contexted_copyright_license_chain | license_branch

    def process_file(self, input_path: Path) -> bool:
        try:
            print(f'Parsing: {input_path}')
            file_content = input_path.read_text(encoding="utf-8")
            self.file_data = file_content
            result = self.entry_point.invoke({})

            if isinstance(result, RustCodeLlmOutput):
                rust_output_file = get_unique_filepath(RUST_FOLDER / f"{input_path.stem}.rs")
                rust_output_file.write_text(result.code, encoding="utf-8")
            else:
                output_file = get_unique_filepath(OUTPUT_FOLDER / f"{input_path.stem}.txt")
                json_str = result.model_dump_json(indent=4)
                output_file.write_text(json_str, encoding="utf-8")

        except Exception as e:
            error_output_file = self._get_error_log_path(input_path.stem)
            error_output_file.write_text(prepare_traceback_text(e), encoding="utf-8")
            return False

        return True
