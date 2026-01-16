import argparse
import os


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="arch.py",
        description=(
            "Архиватор/распаковщик на Python 3.14\n"
            "Алгоритм по расширению: .zst -> zstd, .bz2 -> bz2\n"
            "Директории упаковываются через tarfile"
        ),
    )

    parser.add_argument(
        "source",
        help="Источник: файл/директория (для сжатия) или архив (.zst/.bz2) для распаковки",
    )
    parser.add_argument(
        "destination",
        nargs="?",
        help="Куда писать результат. При сжатии — целевой архив. При распаковке — файл/директория.",
    )

    parser.add_argument(
        "-b", "--benchmark",
        action="store_true",
        help="Вывести время выполнения операции."
    )

    parser.add_argument(
        "-x", "--extract",
        action="store_true",
        help="Принудительный режим распаковки"
    )

    parser.add_argument(
        "--level",
        type=int,
        default=None,
        help="Уровень сжатия для Zstandard"
    )

    return parser.parse_args(argv)


def decide_mode(source: str, dest: str | None, force_extract: bool):
    """
    Определение режима.
    """
    if force_extract:
        return "extract"

    if os.path.isfile(source) and source.lower().endswith((".zst", ".bz2")):
        if dest and dest.lower().endswith((".zst", ".bz2")):
            return "compress"
        return "extract"

    return "compress"
