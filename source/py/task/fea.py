from source.py.feature import generate_fea_string, generate_fea_string_cn_only
from source.py.utils import joinPaths


def write_to_file(file_path: str, content: str, mode: str = "w") -> None:
    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file path. Please provide a valid string path.")
    if not isinstance(content, str):
        raise ValueError("Invalid content. Content must be a string.")

    with open(file_path, encoding="utf-8", mode=mode) as file:
        file.write(content)


def fea(output: str):
    write_to_file(joinPaths(output, "regular.fea"), generate_fea_string(False, False))
    write_to_file(joinPaths(output, "italic.fea"), generate_fea_string(True, False))

    write_to_file(joinPaths(output, "regular_cn.fea"), generate_fea_string(False, True))
    write_to_file(joinPaths(output, "italic_cn.fea"), generate_fea_string(True, True))

    write_to_file(joinPaths(output, "cn.fea"), generate_fea_string_cn_only())
