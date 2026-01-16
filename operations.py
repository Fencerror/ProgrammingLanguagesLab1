import os
import tempfile
import tarfile
from backend import get_algorithm, open_compressed
from utils import progress_bar

CHUNK_SIZE = 1024 * 1024  # 1MiB


def default_archive_name_for_source(source: str) -> str:
    base = os.path.basename(os.path.normpath(source))
    if os.path.isdir(source):
        base += ".tar"
    return base + ".zst"


def copy_stream_with_progress(src, dst, prefix="", total=None):
    done = 0
    while True:
        chunk = src.read(CHUNK_SIZE)
        if not chunk:
            break
        dst.write(chunk)
        done += len(chunk)
        progress_bar(done, total, prefix)

    print()


def compress_file(source: str, dest: str, level=None):
    algo = get_algorithm(dest)
    total = os.path.getsize(source)
    print(f"Сжатие файла {source!r} -> {dest!r} ({algo})")

    with open(source, "rb") as f_in, open_compressed(dest, "wb", algo, level) as f_out:
        copy_stream_with_progress(f_in, f_out, prefix="compress", total=total)


def compress_directory(source: str, dest: str, level=None):
    algo = get_algorithm(dest)
    print(f"Архивация директории {source!r} -> tar -> {dest!r} ({algo})")

    class CountingWriter:
        def __init__(self, wrapped):
            self.wrapped = wrapped
            self.done = 0

        def write(self, chunk: bytes):
            n = self.wrapped.write(chunk)
            self.done += n
            progress_bar(self.done, None, prefix="tar+compress")
            return n

        def flush(self):
            return self.wrapped.flush()

    with open_compressed(dest, "wb", algo, level) as comp:
        cw = CountingWriter(comp)
        with tarfile.open(fileobj=cw, mode="w|") as tar:
            tar.add(source, arcname=os.path.basename(source))

    print()


def decompress_to_temp(archive: str) -> str:
    algo = get_algorithm(archive)
    size = os.path.getsize(archive)

    print(f"Распаковка архива {archive!r} ({algo}) -> временный файл")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        with open_compressed(archive, "rb", algo) as f_in:
            copy_stream_with_progress(f_in, tmp, prefix="decompress", total=size)

    return tmp_path


def extract_from_temp(tmp_path: str, archive_path: str, dest: str | None):
    is_tar = tarfile.is_tarfile(tmp_path)

    if is_tar:
        if dest is None:
            name = os.path.basename(archive_path)
            for ext in (".zst", ".bz2"):
                if name.endswith(ext):
                    name = name[: -len(ext)]
            if name.endswith(".tar"):
                name = name[:-4]
            dest = os.path.join(os.path.dirname(archive_path), name)

        print(f"Обнаружен TAR. Извлечение в {dest!r}")
        os.makedirs(dest, exist_ok=True)
        with tarfile.open(tmp_path, "r:*") as tar:
            tar.extractall(dest)
        os.remove(tmp_path)

    else:
        if dest is None:
            name = os.path.basename(archive_path)
            for ext in (".zst", ".bz2"):
                if name.endswith(ext):
                    name = name[: -len(ext)]
            dest = os.path.join(os.path.dirname(archive_path), name)

        print(f"Запись распакованного файла -> {dest!r}")
        parent = os.path.dirname(os.path.abspath(dest)) or "."
        os.makedirs(parent, exist_ok=True)
        os.replace(tmp_path, dest)
