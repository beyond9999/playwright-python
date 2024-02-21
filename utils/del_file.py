from pathlib import Path
from read_config import Config


def get_directory_paths(base_path, config):
    return [base_path.joinpath(config["PATH"][dir_key]) for dir_key in ["SnapshotDir", "ResultDir", "LogDir"]]


def delete_files(directory_paths, extensions):
    deleted_files = []
    for directory_path in directory_paths:
        for extension in extensions:
            files = list(directory_path.rglob(f"*{extension}"))
            for file_path in files:
                try:
                    file_path.unlink()
                    deleted_files.append(file_path)
                except (PermissionError, FileNotFoundError) as e:
                    print(f"删除时发生错误 {file_path}: {e}")
    return deleted_files


def t_delete(base_path, config):
    directory_paths = get_directory_paths(base_path, config)
    extensions = [".png", ".json", ".txt", ".log"]
    deleted_files = delete_files(directory_paths, extensions)
    return deleted_files


if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parent.parent
    config = Config()()
    deleted_files = t_delete(BASE_PATH, config)
    print(f"已删除文件数: {len(deleted_files)}")
