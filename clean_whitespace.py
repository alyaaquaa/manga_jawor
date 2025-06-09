import os

# Rozszerzenia plików do przetworzenia
ALLOWED_EXTENSIONS = {'.html', '.htm', '.py', '.css', '.js', '.jinja2'}

def clean_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Usuwamy spacje z końca każdej linii
        cleaned_lines = [line.rstrip() + '\n' for line in lines]

        # Usuwamy puste linie na końcu pliku, ale zostawiamy jedną
        while cleaned_lines and cleaned_lines[-1].strip() == '':
            cleaned_lines.pop()
        cleaned_lines.append('\n')

        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(cleaned_lines)

        print(f"✔️ Oczyszczono: {path}")
    except Exception as e:
        print(f"❌ Błąd przy pliku {path}: {e}")

def clean_whitespace_in_project(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                full_path = os.path.join(dirpath, filename)
                clean_file(full_path)

if __name__ == "__main__":
    root_directory = "."  # aktualny katalog
    clean_whitespace_in_project(root_directory)

