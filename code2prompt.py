import json
import os
import sys


def load_mapping():
    """Загружает маппинг языков из JSON-файла рядом со скриптом или EXE."""
    if getattr(sys, "frozen", False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

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
            print(f"Предупреждение: Не удалось прочитать JSON ({e}).")

    return default_mapping


def merge_code_to_markdown(directories):
    """Рекурсивно обходит указанные директории, собирает файлы на основе JSON-конфига и объединяет их в Markdown."""
    lang_mapping = load_mapping()
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
        for root, _, files in os.walk(normalized_dir):
            for f in files:
                if f.endswith(extensions) and f != output_name:
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
    if len(sys.argv) < 2:
        print("Использование: code2prompt.exe <путь_к_папке1> <путь_к_папке2> ...")
        sys.exit(1)

    merge_code_to_markdown(sys.argv[1:])