from cli import parse_args, decide_mode
from operations import (
    compress_file,
    compress_directory,
    decompress_to_temp,
    extract_from_temp,
    default_archive_name_for_source
)
import time
import os
import sys


def main(argv=None):
    args = parse_args(argv)

    source = args.source
    dest = args.destination
    benchmark = args.benchmark
    level = args.level

    mode = decide_mode(source, dest, args.extract)

    start = time.perf_counter() if benchmark else None

    try:
        if mode == "compress":
            if not os.path.exists(source):
                raise FileNotFoundError(f"Источник не найден: {source!r}")

            if dest is None:
                dest = default_archive_name_for_source(source)
                print(f"Целевой архив не задан. Используется: {dest!r}")

            if os.path.isdir(source):
                compress_directory(source, dest, level)
            else:
                compress_file(source, dest, level)

        else:
            if not os.path.isfile(source):
                raise FileNotFoundError(f"Архив не найден: {source!r}")
            tmp = decompress_to_temp(source)
            extract_from_temp(tmp, source, dest)

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

    finally:
        if benchmark:
            elapsed = time.perf_counter() - start
            print(f"Время выполнения: {elapsed:.3f} сек", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
