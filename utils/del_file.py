from pathlib import Path
from read_config import Config


def get_directory_paths(base_path, conf):
    return [base_path.joinpath(conf["PATH"][dir_key]) for dir_key in ["SnapshotDir", "ResultDir", "LogDir"]]


def delete_files(directory_paths, extensions):
    delete_file = []
    for directory_path in directory_paths:
        for extension in extensions:
            files = list(directory_path.rglob(f"*{extension}"))
            for file_path in files:
                try:
                    file_path.unlink()
                    delete_file.append(file_path)
                except (PermissionError, FileNotFoundError) as e:
                    print(f"删除时发生错误 {file_path}: {e}")
    return delete_file


def t_delete(base_path, conf):
    directory_paths = get_directory_paths(base_path, conf)
    extensions = [".png", ".json", ".txt", ".log"]
    files = delete_files(directory_paths, extensions)
    return files


if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parent.parent
    config = Config()()
    deleted_files = t_delete(BASE_PATH, config)
    print(f"已删除文件数: {len(deleted_files)}")
