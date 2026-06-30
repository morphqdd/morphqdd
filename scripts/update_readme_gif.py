import re
import sys

HEADER_IMG_PATTERN = re.compile(r'(<img height="" src=")[^"]+("\s*/>)')


def update_readme_gif(text: str, new_url: str) -> str:
    new_text, count = HEADER_IMG_PATTERN.subn(
        lambda m: m.group(1) + new_url + m.group(2), text, count=1
    )
    if count == 0:
        raise ValueError("header <img> tag not found")
    return new_text


def main() -> None:
    new_url = sys.argv[1]
    readme_path = sys.argv[2] if len(sys.argv) > 2 else "README.md"
    with open(readme_path, encoding="utf-8") as f:
        text = f.read()
    updated = update_readme_gif(text, new_url)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    main()
