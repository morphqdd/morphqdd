import json
import sys


def select_gif(count: int, rules: dict) -> str:
    if count > 0 and count % 5 == 0:
        return rules["div5"]
    if count > 0 and count % 3 == 0:
        return rules["div3"]
    if count > 0 and count % 2 == 0:
        return rules["div2"]
    return rules["default"]


def main() -> None:
    count = int(sys.argv[1])
    rules_path = sys.argv[2]
    with open(rules_path, encoding="utf-8") as f:
        rules = json.load(f)
    print(select_gif(count, rules))


if __name__ == "__main__":
    main()
