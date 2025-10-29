from unittest.mock import AsyncMock
import pytest
from processors.async_graph_file_processor import FileProcessingState


@pytest.mark.asyncio
class TestAsyncGraphFileProcessor:

    async def test_process_file_creates_json(self, async_processor, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass", encoding="utf-8")
        async_processor.graph.ainvoke = AsyncMock(
            return_value=FileProcessingState(
                copyright_info={"holder": "Test"},
                is_license_open_source=False,
                total_func_num=1,
                functions_list=[{"function_name": "foo", "args_count": 1}],
                rust_code='',
                errors=[]
            )
        )
        res = await async_processor.process_file(test_file)
        assert res is True

        # Проверяем в tmp_path, где патчится процессор
        output_files = list(tmp_path.glob(f"{test_file.stem}.json"))
        assert output_files
        content = output_files[0].read_text(encoding="utf-8")
        print(content)
        assert '"functions_list"' in content

    async def test_process_file_creates_rust(self, async_processor, tmp_path):
        test_file = tmp_path / "test.rs"
        test_file.write_text("some code", encoding="utf-8")

        res = await async_processor.process_file(test_file)
        assert res is True

        rust_files = list(tmp_path.glob(f"{test_file.stem}.rs"))
        assert rust_files
        content = rust_files[0].read_text(encoding="utf-8")
        print(content)
        assert "fn main()" in content

    async def test_process_file_handles_exceptions(self, async_processor, tmp_path):
        test_file = tmp_path / "bad_input.py"
        test_file.write_text("bad code", encoding="utf-8")

        async_processor.graph.ainvoke = AsyncMock(side_effect=Exception("Test error"))

        res = await async_processor.process_file(test_file)
        assert res is False

        error_logs = list(tmp_path.glob(f"{test_file.stem}.txt"))
        assert error_logs
        content = error_logs[0].read_text(encoding="utf-8")
        assert "Test error" in content
