# import hashlib
import pathlib

import bencodepy


class Torrent:
    """ Main Torrent class
    """
    def __init__(self, file_path):
        #  TODO: self.path_to_save should be setter for future
        self.path_to_save = pathlib.Path.cwd()

        # With setter
        self.torrent_path = file_path
        self.data_decoded = self.torrent_path

        # Other
        self.announce = self.data_decoded.get(b'announce')
        self.announce_list = self.data_decoded.get(b'announce-list')
        self.comment = self.data_decoded.get(b'comment')
        self.created_by = self.data_decoded.get(b'created by')
        self.creation_date = self.data_decoded.get(b'creation date')
        self.info = self.data_decoded.get(b'info')

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
    def data_decoded(self, _path: pathlib.Path):
        _bytes: bytes = _path.read_bytes()
        _data = bencodepy.decode(_bytes)

        self.__data_decoded = _data
