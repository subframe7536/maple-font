import json


def write_text(file_path: str, content: str, mode: str = "w") -> None:
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("Invalid file path")
    if not isinstance(content, str):
        raise ValueError("Invalid content")
    with open(file_path, encoding="utf-8", mode=mode, newline="\n") as file:
        file.write(content)


def write_json(file_path: str, data: dict) -> None:
    with open(file_path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)


def read_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
