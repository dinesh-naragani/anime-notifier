import os

def load_set(path: str) -> set[str]:
    if os.path.exists(path):
        return set(open(path).read().splitlines())
    return set()

def save_set(path: str, data: set[str]) -> None:
    with open(path, "w") as f:
        f.write("\n".join(sorted(data)))
