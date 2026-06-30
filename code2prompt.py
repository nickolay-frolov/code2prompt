import json
import os
import sys


def load_mapping(script_dir: str) -> dict[str, str]:
    """Загружает маппинг языков из JSON-файла рядом со скриптом или EXE."""
    config_path = os.path.join(script_dir, "mapping.json")

    default_mapping = {
        ".cs": "csharp",
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".go": "go",
        ".json": "json",
        ".html": "html",
        ".css": "css",
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Предупреждение: Не удалось прочитать маппинг-языков ({e}).")

    return default_mapping


def load_ignore(script_dir: str) -> list[str]:
    """Загружает список директорий-исключений из JSON-файла рядом со скриптом или EXE."""
    ignore_path = os.path.join(script_dir, "ignore.json")

    default_ignore = [
        ".git", 
        ".gitignore",
        ".venv",
        "build",
        "dist",
        ".vscode",
        ".vs",
        "bin",
    ]

    if os.path.exists(ignore_path):
        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
             print(f"Предупреждение: Не удалось прочитать игнор-лист ({e}).")

    return default_ignore


def merge_code_to_markdown(directories: str, lang_mapping: dict[str, str], ignore_list: list[str]):
    """Рекурсивно обходит указанные директории, собирает файлы кода на основе JSON-конфига и объединяет их в Markdown."""
    extensions = tuple(lang_mapping.keys())

    for directory in directories:
        directory = directory.strip('"\'')
        normalized_dir = os.path.normpath(directory)

        if not os.path.exists(normalized_dir):
            print(f"Ошибка: Директория '{directory}' не существует. Пропускаем.")
            continue

        dir_name = os.path.basename(normalized_dir) or "root"
        output_name = f"{dir_name}_combined_code.md"
        output_path = os.path.join(normalized_dir, output_name)

        print(f"Обработка папки: {normalized_dir}")

        files_to_process = []
        for root, dirs, files in os.walk(normalized_dir):
            dirs[:] = [d for d in dirs if d not in ignore_list]

            for f in files:
                if f in ignore_list or f == output_name:
                    continue

                if f.endswith(extensions):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, normalized_dir)
                    rel_path = rel_path.replace(os.sep, "/")
                    files_to_process.append((full_path, rel_path))

        if not files_to_process:
            print("  [-] Файлы с указанными расширениями не найдены.\n")
            continue

        try:
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(f"# Структура слоя: {dir_name}\n\n")

                total_files = len(files_to_process)
                for idx, (full_path, rel_path) in enumerate(files_to_process):
                    try:
                        with open(
                            full_path, "r", encoding="utf-8", errors="replace"
                        ) as infile:
                            content = infile.read()

                        ext = os.path.splitext(full_path)[1].lower()
                        lang = lang_mapping.get(ext, "")

                        outfile.write(f"### Файл: {rel_path}\n")
                        outfile.write(f"```{lang}\n")
                        outfile.write(content)

                        if content and not content.endswith("\n"):
                            outfile.write("\n")

                        outfile.write("```")

                        if idx < total_files - 1:
                            outfile.write("\n\n")
                        else:
                            outfile.write("\n")

                    except Exception as e:
                        print(
                            f"  [!] Не удалось прочитать файл {rel_path}. Ошибка: {e}"
                        )

            print(f"  [+] Успешно! Создан файл: {output_name}\n")

        except Exception as e:
            print(
                f"  [!] Ошибка при создании файла {output_name}. Ошибка: {e}\n"
            )


if __name__ == "__main__":
    paths = sys.argv[1:]
    
    if not paths:
        current_dir = os.getcwd()
        paths = [current_dir]

    if not all(os.path.isdir(path) for path in paths):
        print("Ошибка: Один или несколько указанных путей не являются папками!")
        print("Использование: code2prompt.exe <путь_к_папке1> <путь_к_папке2> ...")
        sys.exit(1)

    if getattr(sys, "frozen", False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    lang_mapping = load_mapping(script_dir)
    ignore_list = load_ignore(script_dir)

    merge_code_to_markdown(paths, lang_mapping, ignore_list)