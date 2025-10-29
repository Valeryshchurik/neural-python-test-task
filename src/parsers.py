from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class BaseInputContext(BaseModel):
    file_data: str = Field(
        description="Here is file data to process. This is read only. Do not change it for whatever reason!"
    )


class BaseOutputContext(BaseModel):
    errors: list[str] = Field(
        description="Add here some comments if you struggle to solve the origin task",
        default=[]
    )


class LicenseInfoLlmOutput(BaseOutputContext):
    copyright_holder: str = Field(description="Field for the copyright holder")
    license_name: str = Field(description="Field for the license name")
    is_license_open_source: bool = Field(description="Answer if the license is open source or not (only True or False)")


class FunctionInfoLlmOutput(BaseModel):
    function_name: str = Field(description="Field for the name of the function")
    args_count: int = Field(description="Field for the number of arguments")


class FunctionsList(BaseOutputContext):
    functions_list: list[FunctionInfoLlmOutput] = Field(
        description="Field for the list of function info objects", default=[],
    )


class FunctionCountLlmOutput(BaseOutputContext):
    total_func_num: int = Field(description="Field for counted number of functions")


class RustCodeLlmOutput(BaseOutputContext):
    code: str = Field(description="Save rust code in this field")


license_info_parser = PydanticOutputParser(pydantic_object=LicenseInfoLlmOutput)
function_extractor_parser = PydanticOutputParser(pydantic_object=FunctionsList)
function_counter_parser = PydanticOutputParser(pydantic_object=FunctionCountLlmOutput)
rust_translator_parser = PydanticOutputParser(pydantic_object=RustCodeLlmOutput)
