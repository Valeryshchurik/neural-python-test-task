from parsers import (
    license_info_parser,
    function_extractor_parser,
    function_counter_parser,
    rust_translator_parser,
)
from prompts import (
    copyright_license_template,
    function_extractor_template,
    function_counter_template,
    rust_translator_template,
)
from settings import OUTPUT_FOLDER, RUST_FOLDER, ERROR_LOG_FOLDER
from utils import get_unique_filepath


class BaseLlmFileProcessor:
    version = 'abstract'

    def __init__(self, llm):
        self.output_folder = OUTPUT_FOLDER / self.version
        self.rust_folder = RUST_FOLDER / self.version
        self.error_log_folder = ERROR_LOG_FOLDER / self.version

        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.rust_folder.mkdir(parents=True, exist_ok=True)
        self.error_log_folder.mkdir(parents=True, exist_ok=True)

        self.llm = llm
        self.copyright_license_chain = copyright_license_template | self.llm | license_info_parser
        self.function_extractor_chain = function_extractor_template | self.llm | function_extractor_parser
        self.function_counter_chain = function_counter_template | self.llm | function_counter_parser
        self.rust_translator_chain = rust_translator_template | self.llm | rust_translator_parser

    def _get_output_path(self, filename):
        return get_unique_filepath(self.output_folder / f"{filename}.json")

    def _get_rust_code_path(self, filename):
        return get_unique_filepath(self.rust_folder / f"{filename}.rs")

    def _get_error_log_path(self, filename):
        return get_unique_filepath(self.error_log_folder / f"{filename}.txt")
