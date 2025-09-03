# file_utils.py

def save_to_textfile(filename: str, content: str, mode: str = "w") -> None:
    """
    Save text content to a file.

    :param filename: Name or path of the text file (e.g., "jobs.txt" or "./data/jobs.txt").
    :param content: The string content you want to save.
    :param mode: File mode - "w" = overwrite, "a" = append.
    """
    try:
        with open(filename, mode, encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"✅ Saved content to {filename}")
    except Exception as e:
        print(f"❌ Error saving file {filename}: {e}")
