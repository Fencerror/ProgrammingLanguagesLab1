import sys


def human_size(num: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TiB"


def progress_bar(done: int, total: int | None, prefix=""):
    if total:
        percent = done / total
        width = 30
        filled = int(percent * width)
        bar = "#" * filled + "-" * (width - filled)
        sys.stdout.write(
            f"\r{prefix} [{bar}] {percent*100:5.1f}% ({human_size(done)}/{human_size(total)})"
        )
    else:
        sys.stdout.write(f"\r{prefix} {human_size(done)} processed")

    sys.stdout.flush()
