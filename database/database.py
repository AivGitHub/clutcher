import sqlite3
import pathlib

from clutcher import settings
from database import exception


class Row(sqlite3.Row):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__()

    def get(self, attr, default_value: str = None) -> str:
        try:
            return self[attr]
        except IndexError:
            return default_value


class Database:
    FETCH_MANY_AMOUNT = 100
    DEFAULT_ROW_FACTORY = 'Row'
    _SQL_TORRENT_TABLE = """CREATE TABLE %s torrent (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            torrent_path text,
                                            path_to_save text,
                                            created_by text,
                                            comment text,
                                            creation_date text
                                        )"""

    def __init__(self, db_name: str = settings.NAME) -> None:
        _cwd = pathlib.Path.cwd()

        self.database_path = (_cwd / 'database/data' / f'{db_name}.db').resolve()
        self.connection = self.database_path
        self.cursor = self.connection.cursor()

    @property
    def connection(self) -> sqlite3.Connection:
        return self.__connection

    @connection.setter
    def connection(self, db_path: str, row_factory: str = DEFAULT_ROW_FACTORY) -> None:
        _connection = sqlite3.connect(db_path)

        if row_factory == self.DEFAULT_ROW_FACTORY:
            _connection.row_factory = Row
        else:
            raise exception.WrongRowFactoryException(f'Wrong row factory: {row_factory}')

        self.__connection = _connection

    def execute(self, query: str, values: tuple = ()) -> None:
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)

        self.connection.commit()

    def create_table(self, query: str = _SQL_TORRENT_TABLE, ignore_existence: bool = True) -> None:
        """

        :param query: Creation query. See _SQL_TORRENT_TABLE example
        :param ignore_existence: if False, then sqlite3.OperationalError: table torrent already exists is raised
        :raise: database.exception.WrongQueryException if query does not contain %s for "IF NOT EXISTS" block
        :raise: sqlite3.OperationalError if ignore_existence = False
        :return: None

        TODO: Change to universal way
        """
        _if_not_exists = ''

        if query and '%s' not in query:
            raise exception.WrongQueryException('Query must contain \'%s\'')

        if ignore_existence:
            _if_not_exists = 'IF NOT EXISTS'

        self.execute(query % _if_not_exists)

    def secure_fetchall(self, query: str) -> list:
        _executed = self.cursor.execute(query)
        _next = _executed.fetchmany(self.FETCH_MANY_AMOUNT)

        while _next:
            mapped_rows = self.rows_mapper(_next)
            _next = _executed.fetchmany(self.FETCH_MANY_AMOUNT)

            yield mapped_rows

    def delete_all_data(self):
        self.execute('DELETE FROM torrent')

    @classmethod
    def rows_mapper(cls, rows: list) -> list:
        mapped_rows = []

        for row in rows:
            _keys = row.keys()
            _values = [row.get(key) for key in _keys]
            _zipped = zip(_keys, _values)

            mapped_rows.append(dict(_zipped))

        return mapped_rows

    def close(self) -> None:
        self.connection.close()
