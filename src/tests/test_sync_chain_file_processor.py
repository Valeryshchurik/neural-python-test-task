from unittest.mock import MagicMock
from parsers import RustCodeLlmOutput


class TestSyncChainFileProcessor:

    def test_process_file_creates_json(self, processor, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass", encoding="utf-8")

        processor.entry_point.invoke.return_value = MagicMock(
            model_dump_json=lambda indent=4: '{"functions_list": [{"function_name": "foo"}]}'
        )

        result = processor.process_file(test_file)
        assert result is True

        output_files = list(tmp_path.glob(f"{test_file.stem}.json"))
        assert output_files
        content = output_files[0].read_text(encoding="utf-8")
        assert '"functions_list"' in content

    def test_process_file_creates_rust(self, processor, tmp_path):
        test_file = tmp_path / "test.rs"
        test_file.write_text("some rust code", encoding="utf-8")

        rust_obj = RustCodeLlmOutput(code="fn main() {}")
        processor.entry_point.invoke.return_value = rust_obj

        result = processor.process_file(test_file)
        assert result is True

        rust_files = list(tmp_path.glob(f"{test_file.stem}.rs"))
        assert rust_files
        content = rust_files[0].read_text(encoding="utf-8")
        assert "fn main()" in content

    def test_process_file_handles_exception(self, processor, tmp_path):
        test_file = tmp_path / "bad_input.py"
        test_file.write_text("bad code", encoding="utf-8")

        processor.entry_point.invoke = MagicMock(side_effect=Exception("Test error"))

        result = processor.process_file(test_file)
        assert result is False

        error_logs = list(tmp_path.glob(f"{test_file.stem}.txt"))
        assert error_logs
        content = error_logs[0].read_text(encoding="utf-8")
        assert "Test error" in content
