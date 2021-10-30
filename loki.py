import argparse
import pathlib
import tqdm
import dotenv
import os

dotenv.load_dotenv()

def move(original: pathlib.Path, new: pathlib.Path, chunk_size: int) -> None:
    with original.open(mode='rb') as old_file, new.open(mode='wb') as new_file, \
    tqdm.tqdm(total=original.stat().st_size, unit_scale=True, unit='b') as progress:
        for chunk in iter(lambda: old_file.read(chunk_size), b''):
            new_file.write(chunk)
            progress.update(len(chunk))

    original.unlink()

parser = argparse.ArgumentParser(description='Use this configure the Chia Plotting process.')
parser.add_argument(
    'count',
    help='Number of plots to create'
)
parser.add_argument(
    'temp-1',
    type=pathlib.Path,
    dest='temp_1',
    help='Temporary directory, needs ~220 GiB'
)
parser.add_argument(
    'finaldir',
    type=pathlib.Path,
    help='Final directory to move to.'
)
parser.add_argument(
    '-2', '--temp-2',
    type=pathlib.Path,
    dest='temp_2',
    help='Temporary directory 2, needs ~110 GiB [RAM] (default =<temp-1>)'
)
parser.add_argument(
    '-3', '--temp-3',
    type=pathlib.Path,
    dest='temp_3',
    help='Where to write plots to.'
)
parser.add_argument(
    '-t', '--threads',
    type=int,
    help='Number of threads',
    default=os.cpu_count()
)
parser.add_argument(
    '-p', '--poolkey',
    help='Pool Public Key (48 bytes)',
    default=os.environ.get('pool-key')
)
parser.add_argument(
    '-f', '--farmerkey',
    help='Farmer Public Key (48 bytes)',
    default=os.environ.get('farmer-key')
)

config = parser.parse_args()

class StoreAndStdout(io.TextIOBase):
    def write(self, text):
        print(text)
        if not hasattr('self', '_text'):
            self._text = ''
        self._text += text

    def read(self):
        return self._text

chia_plotter = pathlib.Path('chia_plot')
if not chia_plotter.exists():
    raise FileNotFoundError('Could not find Chia Plotter binary.')
