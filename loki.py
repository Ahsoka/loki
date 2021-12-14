import subprocess
import threading
import argparse
import datetime
import pathlib
import dotenv
import tqdm
import sys
import os
import io
import re

dotenv.load_dotenv()

def move(original: pathlib.Path, new: pathlib.Path, chunk_size: int = 65_536) -> None:
    with original.open(mode='rb') as old_file, new.open(mode='wb') as new_file, \
    tqdm.tqdm(total=original.stat().st_size, unit_scale=True, unit='b') as progress:
        for chunk in iter(lambda: old_file.read(chunk_size), b''):
            new_file.write(chunk)
            progress.update(len(chunk))

    original.unlink()

parser = argparse.ArgumentParser(description='Use this configure the Chia Plotting process.')
parser.add_argument(
    'count',
    type=int,
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

class StoreAndStdout(io.TextIOWrapper):
    def write(self, text):
        with open('.log', 'a') as log:
            log.write(text)
        if not hasattr('self', '_text'):
            self._text = ''
        self._text += text
        super().write(text)

    def read(self):
        return self._text

chia_plotter = pathlib.Path('chia_plot').absolute()
if not chia_plotter.exists():
    raise FileNotFoundError('Could not find Chia Plotter binary.')

stream = StoreAndStdout(sys.stdout)
for _ in range(config.count):
    current_date = datetime.date.today()
    plot = subprocess.Popen(
        (f"/.{chia_plotter}, -t {config.temp_1} -2 {config.temp_2} -d {config.temp_3} "
        f"-t {config.threads} -p {config.poolkey} -f {config.farmerkey}").split(),
        stdout=stream,
        stderr=stream,
        text=True
    )
    plot.wait()

    plot_name = re.search(
        fr"plot-k32-{format(current_date, '%Y-%m-%d')}-\d{{2}}-\d{{2}}-\w{{64}}",
        stream.read()
    )
    if plot_name:
        plot_name = plot_name[0]
    else:
        raise RuntimeError('Could not determine the name of the plot that was just created.')

    thread = threading.Thread(
        target=move,
        args=(
            config.temp_3 / plot_name,
            config.finaldir / plot_name
        )
    )
    thread.start()
