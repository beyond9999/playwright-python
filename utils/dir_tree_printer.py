import os


def print_directory_structure(directory, indent=0):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if item.endswith('.pyc') or (
                os.path.isdir(item_path) and any(f.endswith('.pyc') for f in os.listdir(item_path))):
            continue  # 跳过.pyc文件和包含.pyc文件的目录
        if os.path.isdir(item_path):
            print("  " * indent + f"📁 {item}")
            print_directory_structure(item_path, indent + 1)
        else:
            print("  " * indent + f"📄 {item}")


if __name__ == "__main__":
    project_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print_directory_structure(project_directory)
