from settings import OUTPUT_FOLDER, RUST_FOLDER, ERROR_LOG_FOLDER


def print_process_finished_message(results):
    succeeded_files_count = sum(results)
    failed_files_count = len(results) - succeeded_files_count

    dirs_to_check = [OUTPUT_FOLDER, RUST_FOLDER]
    if failed_files_count:
        dirs_to_check.append(ERROR_LOG_FOLDER)
    print(
        f'Files parsed. Successful: {succeeded_files_count}. Failed: {failed_files_count}. Check the following dirs: '
    )
    for folder in dirs_to_check:
        print(folder)
