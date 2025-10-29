from unittest.mock import AsyncMock, MagicMock
import pytest
from processors.async_graph_file_processor import AsyncGraphFileProcessor, FileProcessingState
from processors.sync_chain_file_processor import SyncChainFileProcessor


@pytest.fixture
def mock_sync_llm():
    llm = MagicMock()
    llm.__or__.side_effect = lambda other: other
    return llm


@pytest.fixture
def mock_async_llm():
    llm = AsyncMock()
    llm.__or__.side_effect = lambda other: other
    return llm


class EntryPointMock:
    def __init__(self):
        self.invoke = MagicMock()

@pytest.fixture
def processor(mock_sync_llm, tmp_path):
    p = SyncChainFileProcessor(mock_sync_llm)

    p.entry_point = EntryPointMock()

    p._get_output_path = lambda filename: tmp_path / f"{filename}.json"
    p._get_rust_code_path = lambda filename: tmp_path / f"{filename}.rs"
    p._get_error_log_path = lambda filename: tmp_path / f"{filename}.txt"

    return p


@pytest.fixture
def async_processor(mock_async_llm, tmp_path):
    p = AsyncGraphFileProcessor(mock_async_llm)

    p.graph.ainvoke = AsyncMock(
        return_value=FileProcessingState(
            copyright_info={"holder": "Test"},
            is_license_open_source=True,
            total_func_num=3,
            functions_list=[{"function_name": "foo", "args_count": 1}],
            rust_code="fn main() {}",
            errors=[]
        )
    )
    p._get_output_path = lambda filename: tmp_path / f"{filename}.json"
    p._get_rust_code_path = lambda filename: tmp_path / f"{filename}.rs"
    p._get_error_log_path = lambda filename: tmp_path / f"{filename}.txt"

    return p
