from processors.base_llm_file_processor import BaseLlmFileProcessor


def print_process_finished_message(llm_processor: BaseLlmFileProcessor, results):
    succeeded_files_count = sum(results)
    failed_files_count = len(results) - succeeded_files_count

    dirs_to_check = [llm_processor.output_folder, llm_processor.rust_folder]
    if failed_files_count:
        dirs_to_check.append(llm_processor.error_log_folder)
    print(
        f'Files parsed. Successful: {succeeded_files_count}. Failed: {failed_files_count}. Check the following dirs: '
    )
    for folder in dirs_to_check:
        print(folder)
