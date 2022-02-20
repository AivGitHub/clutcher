# Copyright (c) 2022, Ivan Koldakov.
# All rights reserved.
#
# Use as you want, modify as you want but please include the author's name.

import argparse
import pathlib
import sys

from PyQt5.QtWidgets import QApplication

from clutcher.maintain import Maintain
from database.database import Database
from ui.gui import MainFrame


def run() -> None:
    parser = argparse.ArgumentParser(description='Download files.')

    files = []
    _files_nargs = argparse.ONE_OR_MORE

    # TODO: replace it with something better
    if '-g' in sys.argv or '--gui' in sys.argv:
        _files_nargs = argparse.ZERO_OR_MORE

    if not sys.stdin.isatty():
        files = [line.strip() for line in sys.stdin.readlines() if line.strip()]

        if files:
            _files_nargs = argparse.ZERO_OR_MORE

    parser.add_argument('files',
                        type=str,
                        nargs=_files_nargs,
                        help='File paths')

    parser.add_argument('-d', '--detach',
                        required=False,
                        help='Detach mode',
                        action='store_true')

    parser.add_argument('-g', '--gui',
                        required=False,
                        help='Run gui application',
                        action='store_true')

    parser.add_argument('-db', '--database',
                        required=False,
                        help='Use database',
                        action='store_true')

    parser.add_argument('-ddb', '--drop_database',
                        required=False,
                        help='Drop database. Terminates program execution',
                        action='store_true')

    parser.add_argument('-ddbd', '--drop_database_data',
                        required=False,
                        help='Drop all database data',
                        action='store_true')

    _args = parser.parse_args()
    dict_args = vars(_args)
    _tty_files = dict_args.get('files')

    if _tty_files:
        files.extend(_tty_files)

    dict_args.update({'files': files})

    if dict_args.get('database'):
        # Database block
        database = Database()

        if dict_args.get('drop_database_data'):
            database.delete_all_data()

        if dict_args.get('drop_database'):
            database_path = database.database_path
            database.close()

            pathlib.Path(database_path).unlink()

            return None

        database.create_table()
        database.close()

    if dict_args.get('gui'):
        app = QApplication([])
        main_frame = MainFrame(**dict_args)
        main_frame.show()
        sys.exit(app.exec_())
    else:
        maintain = Maintain(**dict_args)
        maintain.start()


if __name__ == '__main__':
    run()
