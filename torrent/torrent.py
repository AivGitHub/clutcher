import hashlib
import pathlib
import time

from bcoding import bencode, bdecode


class Torrent:
    # Torrent files constant attributes
    _ANNOUNCE = 'announce'
    _ANNOUNCE_LIST = 'announce-list'
    _COMMENT = 'comment'
    _CREATION_DATE = 'creation date'
    _FILES = 'files'
    _INFO = 'info'
    _NAME = 'name'
    _PATH = 'path'
    _LENGTH = 'length'
    _PIECES = 'pieces'
    _PIECE_LENGTH = 'piece length'

    def __init__(self, file_path) -> None:
        # Init variables
        self.total_length: int = 0
        self.files: list = []
        self.path_to_save = pathlib.Path.cwd()
        # self.path_to_save = pathlib.Path.home()

        # With setter
        self.torrent_path = file_path
        self.torrent_file_data = self.torrent_path
        self.announce_list = self.torrent_file_data

        # From torrent_file_data
        self.torrent_comment = self.torrent_file_data.get(self._COMMENT)
        self.torrent_creation_date = self.torrent_file_data.get(self._CREATION_DATE)
        self.torrent_info = self.torrent_file_data.get(self._INFO)

        # From torrent_file_data.info
        self.piece_length = self.torrent_info.get(self._PIECE_LENGTH)
        self.pieces = self.torrent_info.get(self._PIECES)
        self.name = self.torrent_info.get(self._NAME)

        # With setter from self.torrent_info
        self.info_hash = self.torrent_info

        # With setter other
        self.peer_id = str(time.time())

        # Set dependent data
        # Sets self.files and self.total_length
        self.set_files()

    def __str__(self) -> str:
        return str(self.torrent_path)

    @property
    def torrent_path(self) -> pathlib.Path:
        return self.__torrent_path

    @torrent_path.setter
    def torrent_path(self, _path: str) -> None:
        path = pathlib.Path(_path).resolve()

        if not path.exists():
            # Just in case
            raise FileNotFoundError(f'File {str(path)} does not exist.')

        self.__torrent_path = path

    @property
    def torrent_file_data(self) -> dict:
        return self.__torrent_file_data

    @torrent_file_data.setter
    def torrent_file_data(self, _path: pathlib.Path):
        _bytes = _path.read_bytes()
        _data = bdecode(_bytes)

        self.__torrent_file_data = _data

    @property
    def announce_list(self) -> list:
        return self.__announce_list

    @announce_list.setter
    def announce_list(self, _torrent_file_data: dict):
        _announce_list = []

        if self._ANNOUNCE_LIST in _torrent_file_data:
            _announce_list = _torrent_file_data.get(self._ANNOUNCE_LIST)
        else:
            _announce_list = [[_torrent_file_data.get(self._ANNOUNCE)]]

        self.__announce_list = _announce_list

    @property
    def info_hash(self) -> bytes:
        return self.__info_hash

    @info_hash.setter
    def info_hash(self, torrent_info: dict):
        _bencoded = bencode(torrent_info)

        self.__info_hash = hashlib.sha1(_bencoded).digest()

    @property
    def peer_id(self) -> bytes:
        return self.__peer_id

    @peer_id.setter
    def peer_id(self, seed: str):
        self.__peer_id = hashlib.sha1(seed.encode('utf-8')).digest()

    def set_files(self) -> None:
        if self._FILES not in self.torrent_info:
            self.files.append({
                self._PATH: self.name,
                self._LENGTH: self.torrent_info.get(self._LENGTH)
            })
            self.total_length = self.torrent_info.get(self._INFO)
            return None

        for file in self.torrent_info.get(self._FILES):
            _file_name = pathlib.Path(*file.get(self._PATH))
            _file_path = (self.path_to_save / self.name / _file_name).resolve()

            self.files.append({
                self._PATH: _file_path,
                self._LENGTH: file.get(self._LENGTH)
            })
            self.total_length += file.get(self._LENGTH)
