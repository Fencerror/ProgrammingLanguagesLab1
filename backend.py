from compression import bz2, zstd


def get_algorithm(path: str) -> str:
    low = path.lower()
    if low.endswith(".zst"):
        return "zstd"
    if low.endswith(".bz2"):
        return "bz2"
    raise ValueError(
        f"Невозможно определить алгоритм по расширению: {path!r}. "
        f"Ожидается .zst или .bz2"
    )


def open_compressed(path: str, mode: str, algorithm: str, level=None):
    if algorithm == "zstd":
        return zstd.open(path, mode=mode, level=level)
    elif algorithm == "bz2":
        return bz2.open(path, mode=mode)
    else:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")
