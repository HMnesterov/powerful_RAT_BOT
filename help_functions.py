def get_files_and_dirs_in_directories(file_directory):
    files = []
    directories = []

    for x in file_directory.iterdir():
        if x.is_dir():
            directories.append(x)
        elif x.is_file():
            files.append(x)
    return {'files': files, 'directories': directories}

