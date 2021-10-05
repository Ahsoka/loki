import pathlib
import tqdm

def move(original: pathlib.Path, new: pathlib.Path, chunk_size: int) -> None:
    with original.open(mode='rb') as old_file, new.open(mode='wb') as new_file, \
    tqdm.tqdm(total=original.stat().st_size, unit_scale=True, unit='b') as progress:
        for chunk in iter(lambda: old_file.read(chunk_size), b''):
            new_file.write(chunk)
            progress.update(len(chunk))

    original.unlink()
