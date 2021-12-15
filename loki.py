import threading
import argparse
import datetime
import pathlib
import inspect
import tqdm
import sys
import re

def move(original: pathlib.Path, new: pathlib.Path, progress: tqdm.tqdm, chunk_size: int = 65_536) -> None:
    with original.open(mode='rb') as old_file, (new / original.name).open(mode='wb') as new_file:
        for chunk in iter(lambda: old_file.read(chunk_size), b''):
            new_file.write(chunk)
            progress.update(len(chunk))

    original.unlink()
    progress.close()

parser = argparse.ArgumentParser()
parser.add_argument(
    'location',
    type=pathlib.Path,
    help='Location to move the plot after it is created.'
)
parser.add_argument(
    '--log-file',
    type=pathlib.Path,
    help='Location of the log file.',
    default='chia.log',
    dest='log_file'
)
parser.add_argument(
    '--chunk-size',
    type=int,
    help='Chunk size used when transferring plots.',
    dest='chunk_size',
    default=dict(inspect.signature(move).parameters.items())['chunk_size'].default
)
config = parser.parse_args()

logs = ''
plot_names = []
progress_bar = None
final_dir = None
final_dir_re = re.compile(r"Final Directory: (~?/?([-\w ]+/)+)")
try:
    for line in sys.stdin:
        logs += line
        tqdm.tqdm.write(line)
        if final_dir is None:
            if search := final_dir_re.search(line):
                final_dir = search[1]

        if line.startswith('Plot Name:'):
            current_date = datetime.date.today()
            plot_name = re.search(
                fr"plot-k32-{format(current_date, '%Y-%m-%d')}-\d{{2}}-\d{{2}}-\w{{64}}", line
            )
            if plot_name:
                plot_names.append(plot_name[0])

        # This indicates the plot is finished being created and has been moved to the final directory
        if line.startswith('Copy to'):
            if len(plot_names) == 0:
                raise FileNotFoundError('Plot name could not be identified')
            elif final_dir is None:
                raise FileNotFoundError('Final directory could not be identified')
            plot = pathlib.Path(final_dir) / plot_names[0]
            plot_names.pop(0)
            if not plot.exists():
                raise FileNotFoundError(f'Plot not found in expected location: {plot}')

            progress_bar = tqdm.tqdm(total=plot.stat().st_size, unit_scale=True, unit='b')
            thread = threading.Thread(target=move, args=(
                plot,
                config.location,
                progress_bar,
                config.chunk_size
            ))
            thread.start()
finally:
    with config.log_file.open(mode='a') as file:
        file.write(logs)
