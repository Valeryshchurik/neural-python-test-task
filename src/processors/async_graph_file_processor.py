from pathlib import Path
import aiofiles
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
from processors.base_llm_file_processor import BaseLlmFileProcessor
from enum import Enum
from utils import prepare_traceback_text


class NodeNames(Enum):
    LICENSE = "license"
    FUNC_COUNT = "func_count"
    FUNC_EXTRACT = "func_extract"
    RUST_TRANSLATOR = "rust_translator"


class FileProcessingState(BaseModel):
    file_data: str = Field(description="Here is file data to process. This is read only.", default="")
    copyright_info: dict = Field(default=None)
    functions_list: list = Field(default_factory=list)
    total_func_num: int = Field(default=0)
    rust_code: str = Field(default="")
    errors: list = Field(default_factory=list)
    is_license_open_source: bool = Field(default=False)


class AsyncGraphFileProcessor(BaseLlmFileProcessor):
    version = 'llm_async_graph_proc_2'

    def __init__(self, llm):
        super().__init__(llm)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(FileProcessingState)

        async def extract_license(state: FileProcessingState) -> FileProcessingState:
            result = await self.copyright_license_chain.ainvoke({"file_data": state.file_data})
            state.copyright_info = result.dict()
            errors = state.copyright_info.pop('errors')
            state.is_license_open_source = result.is_license_open_source
            state.errors.extend(errors)
            return state

        async def count_functions(state: FileProcessingState) -> FileProcessingState:
            result = await self.function_counter_chain.ainvoke({"file_data": state.file_data})
            state.total_func_num = result.total_func_num
            state.errors.extend(result.errors)
            return state

        async def extract_functions(state: FileProcessingState) -> FileProcessingState:
            result = await self.function_extractor_chain.ainvoke({"file_data": state.file_data})
            state.functions_list = result.functions_list
            state.errors.extend(result.errors)
            return state

        async def rust_translate(state: FileProcessingState) -> FileProcessingState:
            result = await self.rust_translator_chain.ainvoke({"file_data": state.file_data})
            state.rust_code = result.code
            state.errors.extend(result.errors)
            return state

        graph_builder.add_node(NodeNames.LICENSE.value, extract_license)
        graph_builder.add_node(NodeNames.FUNC_COUNT.value, count_functions)
        graph_builder.add_node(NodeNames.FUNC_EXTRACT.value, extract_functions)
        graph_builder.add_node(NodeNames.RUST_TRANSLATOR.value, rust_translate)

        graph_builder.add_edge(START, NodeNames.LICENSE.value)

        def route_after_license(state: FileProcessingState) -> str:
            return NodeNames.FUNC_COUNT.value if state.is_license_open_source else NodeNames.FUNC_EXTRACT.value

        def route_after_func_count(state: FileProcessingState) -> str:
            return NodeNames.FUNC_EXTRACT.value if state.total_func_num > 2 else NodeNames.RUST_TRANSLATOR.value

        graph_builder.add_conditional_edges(NodeNames.LICENSE.value, route_after_license)
        graph_builder.add_conditional_edges(NodeNames.FUNC_COUNT.value, route_after_func_count)

        graph_builder.add_edge(NodeNames.FUNC_EXTRACT.value, END)
        graph_builder.add_edge(NodeNames.RUST_TRANSLATOR.value, END)

        return graph_builder.compile()

    async def process_file(self, input_path: Path):
        try:
            print(f'Parsing: {input_path}')
            async with aiofiles.open(input_path, 'r', encoding="utf-8") as f:
                file_content = await f.read()

            initial_state = FileProcessingState(file_data=file_content)
            final_state_dict = await self.graph.ainvoke(initial_state)
            final_state = FileProcessingState.model_validate(final_state_dict)

            if final_state.rust_code:
                rust_output_file = self._get_rust_code_path(input_path.stem)
                async with aiofiles.open(rust_output_file, mode='w', encoding='utf-8') as f:
                    await f.write(final_state.rust_code)
            else:
                json_str = final_state.model_dump_json(indent=4)
                output_file = self._get_output_path(input_path.stem)
                async with aiofiles.open(output_file, mode='w', encoding='utf-8') as f:
                    await f.write(json_str)

        except Exception as e:
            error_output_file = self._get_error_log_path(input_path.stem)
            async with aiofiles.open(error_output_file, mode='w', encoding='utf-8') as f:
                await f.write(prepare_traceback_text(e))
            return False

        return True
