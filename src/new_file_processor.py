from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from parsers import license_info_parser, function_extractor_parser, function_counter_parser, rust_translator_parser
from prompts import (
    copyright_license_template,
    function_extractor_template,
    function_counter_template,
    rust_translator_template,
)


class FileProcessingState(BaseModel):
    file_data: str = Field(description="Here is file data to process. This is read only.", default="")
    copyright_info: dict = Field(default=None)
    functions_list: list = Field(default_factory=list)
    total_func_num: int = Field(default=0)
    rust_code: str = Field(default="")
    errors: list = Field(default_factory=list)
    is_license_open_source: bool = Field(default=False)


class LlmPyFuncFileProcessor:
    def __init__(self, llm):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(FileProcessingState)

        def extract_license(state: FileProcessingState) -> FileProcessingState:
            result = (copyright_license_template | self.llm | license_info_parser).invoke(
                {"file_data": state.file_data})
            state.copyright_info = result.dict()
            state.is_license_open_source = result.is_license_open_source
            state.errors.extend(result.errors)
            return state

        def count_functions(state: FileProcessingState) -> FileProcessingState:
            result = (function_counter_template | self.llm | function_counter_parser).invoke(
                {"file_data": state.file_data})
            state.total_func_num = result.total_func_num
            state.errors.extend(result.errors)
            return state

        def extract_functions(state: FileProcessingState) -> FileProcessingState:
            result = (function_extractor_template | self.llm | function_extractor_parser).invoke(
                {"file_data": state.file_data})
            state.functions_list = result.functions_list
            state.errors.extend(result.errors)
            return state

        def rust_translate(state: FileProcessingState) -> FileProcessingState:
            result = (rust_translator_template | self.llm | rust_translator_parser).invoke(
                {"file_data": state.file_data})
            state.rust_code = result.code
            state.errors.extend(result.errors)
            return state

        graph_builder.add_node("license", extract_license)
        graph_builder.add_node("func_count", count_functions)
        graph_builder.add_node("func_extract", extract_functions)
        graph_builder.add_node("rust_translator", rust_translate)

        graph_builder.add_edge(START, "license")

        def route_after_license(state: FileProcessingState) -> str:
            return "func_extract" if state.is_license_open_source else "func_count"

        def route_after_func_count(state: FileProcessingState) -> str:
            return "func_extract" if state.total_func_num > 2 else "rust_translator"

        graph_builder.add_conditional_edges("license", route_after_license)
        graph_builder.add_conditional_edges("func_count", route_after_func_count)

        graph_builder.add_edge("func_extract", "rust_translator")
        graph_builder.add_edge("rust_translator", END)

        return graph_builder.compile()

    def process_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        initial_state = FileProcessingState(file_data=file_content)
        final_state = self.graph.invoke(initial_state)
        return final_state
