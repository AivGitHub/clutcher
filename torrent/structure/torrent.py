import hashlib
import pathlib
import time

import bencodepy


class Torrent:
    """ Main Torrent class
    """
    def __init__(self, file_path: str) -> None:
        #  TODO: self.path_to_save should be setter for future
        self.path_to_save = pathlib.Path.cwd()

        # With setter
        self.torrent_path = file_path
        self.data_decoded = self.torrent_path

        # From data_decoded
        self.announce = self.data_decoded.get(b'announce')
        self.announce_list = self.data_decoded.get(b'announce-list')
        self.comment = self.data_decoded.get(b'comment')
        self.created_by = self.data_decoded.get(b'created by')
        self.creation_date = self.data_decoded.get(b'creation date')
        self.info = self.data_decoded.get(b'info')

        # With setter from self.torrent_info
        self.info_hash = self.info
        self.files = self.info
        self.total_length = self.info

        # From self.info
        self.name = self.info.get(b'name')
        self.piece_length = self.info.get(b'piece length')
        self.pieces = self.info.get(b'pieces')

        # Other
        self.peer_id = str(time.time())

    @property
    def torrent_path(self) -> pathlib.Path:
        return self.__torrent_path

    @torrent_path.setter
    def torrent_path(self, _path: str) -> None:
        path = pathlib.Path(_path).resolve()

        if not path.exists():
            raise FileNotFoundError(f'File {str(path)} does not exist.')

        self.__torrent_path = path

    @property
    def data_decoded(self) -> dict:
        return self.__data_decoded

    @data_decoded.setter
    def data_decoded(self, _path: pathlib.Path) -> None:
        _bytes: bytes = _path.read_bytes()
        _data = bencodepy.decode(_bytes)

        self.__data_decoded = _data

    @property
    def peer_id(self) -> bytes:
        return self.__peer_id

    @peer_id.setter
    def peer_id(self, seed: str) -> None:
        self.__peer_id = hashlib.sha1(seed.encode('utf-8')).digest()

    @property
    def info_hash(self) -> bytes:
        return self.__info_hash

    @info_hash.setter
    def info_hash(self, info: dict):
        _encoded = bencodepy.encode(info)

        self.__info_hash = hashlib.sha1(_encoded).digest()

    @property
    def files(self) -> list:
        return self.__files

    @files.setter
    def files(self, info: dict):
        _files: list = []
        _name: bytes = info.get(b'name')
        _name_decoded: str = _name.decode('utf-8')

        if b'files' in info:
            for file in info.get(b'files'):
                _path = [path.decode('utf-8') for path in file.get(b'path')]
                _file_name = pathlib.Path(*_path)
                _file_path = (self.path_to_save / _name_decoded / _file_name).resolve()

                _files.append({
                    'path': _file_path,
                    'length': file.get(b'length')
                })
        else:
            _files.append({
                'path': (self.path_to_save / _name_decoded).resolve(),
                'length': info.get(b'length')
            })

        self.__files = _files

    @property
    def total_length(self) -> int:
        return self.__total_length

    @total_length.setter
    def total_length(self, info: dict) -> None:
        _total_length: int = 0

        if 'files' in info:
            for file in info.get(b'files'):
                _total_length += file.get(b'files')
        else:
            _total_length = info.get(b'length')

        self.__total_length = _total_length

    def get_dict(self):
        return {
            'name': self.name.decode('utf-8'),
            'torrent_path': str(self.torrent_path),
            'path_to_save': str(self.path_to_save),
            'created_by': self.created_by.decode('utf-8'),
            'comment': self.comment.decode('utf-8'),
            'creation_date': self.creation_date
        }
