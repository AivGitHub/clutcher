# Copyright (c) 2022, Ivan Koldakov.
# All rights reserved.
#
# Use as you want, modify as you want but please include the author's name.

import argparse
import sys

from torrent import Torrent


def run() -> None:
    parser = argparse.ArgumentParser(description='Download files.')

    files = []
    _files_nargs = argparse.ONE_OR_MORE

    if not sys.stdin.isatty():
        files = [line.strip() for line in sys.stdin.readlines() if line.strip()]

        if files:
            _files_nargs = argparse.ZERO_OR_MORE

    parser.add_argument('files',
                        type=str,
                        nargs=_files_nargs,
                        help='File paths')

    parser.add_argument('-d', '--detached',
                        required=False,
                        help='Detached mode',
                        action='store_true')

    _args = parser.parse_args()
    dict_args = vars(_args)
    _tty_files = dict_args.get('files')

    if _tty_files:
        files.extend(_tty_files)

    dict_args.update({'files': files})

    pass


if __name__ == '__main__':
    run()
