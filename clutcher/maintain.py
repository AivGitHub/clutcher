from concurrent.futures import ThreadPoolExecutor
import threading

from database.database import Database
from database.exception import WrongSchemeException
from torrent.structure.torrent import Torrent


class Maintain:

    def __init__(self, **kwargs) -> None:
        # kwargs arguments
        self.files = kwargs.get('files')
        self.detach = kwargs.get('detach')
        self.use_database = kwargs.get('database')

        # Other
        self.torrents = [Torrent(file) for file in self.files]

    def process(self, torrent: Torrent) -> None:
        # self.save_to_database(torrent)
        print(f'Task Executed {threading.current_thread()}')

    def start(self) -> None:
        with ThreadPoolExecutor() as executor:
            running_tasks = [executor.submit(self.process, torrent) for torrent in self.torrents]

            for running_task in running_tasks:
                running_task.result()

    def pause(self):
        raise NotImplementedError()

    def resume(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def save_to_database(self, torrent: Torrent, scheme: str = 'torrent') -> None:
        if not self.use_database:
            return None

        database = Database()
        dict_data = torrent.get_dict()
        _keys = dict_data.keys()

        if scheme == 'torrent':
            sql = f'INSERT INTO torrent ({", ".join(_keys)}) VALUES (:{", :".join(_keys)})'
        else:
            raise WrongSchemeException(f'Scheme {scheme} not found')

        database.execute(sql, dict_data)
        database.close()
