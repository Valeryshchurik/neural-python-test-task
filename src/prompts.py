from langchain_core.prompts import PromptTemplate

from parsers import license_info_parser, function_extractor_parser, function_counter_parser, rust_translator_parser

copyright_license_template = PromptTemplate(
    input_variables=["file_data"],
    template=
    """
        Extract copyright holder and license name from the following code:
        {file_data}
        
        Return a strict parseable JSON matching this schema:
        {format_instructions}
    """,
    partial_variables={'format_instructions': license_info_parser.get_format_instructions()}
)

function_extractor_template = PromptTemplate(
    input_variables=["file_data"],
    template=
    """
    Extract all function names and their number of arguments from this code:
    {file_data}
    
        Return a strict parseable JSON matching this schema:
    {format_instructions}
    """,
    partial_variables={'format_instructions': function_extractor_parser.get_format_instructions()}
)

function_counter_template = PromptTemplate(
    input_variables=["file_data"],
    template=
    """
    Count number of functions defined in this code:
    {file_data}
    
        Return a strict parseable JSON matching this schema:
    {format_instructions}
    """,
    partial_variables={'format_instructions': function_counter_parser.get_format_instructions()}
)

rust_translator_template = PromptTemplate(
    input_variables=["file_data"],
    template=
    """
    Rewrite this code into Rust:
    {file_data}
    
    Return the resulted code in a field of the strict parseable JSON matching this schema:
    {format_instructions}
    """,
    partial_variables={'format_instructions': rust_translator_parser.get_format_instructions()}
)
