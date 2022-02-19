from concurrent.futures import ThreadPoolExecutor
import threading

from torrent.structure.torrent import Torrent


class Maintain:

    def __init__(self, **kwargs) -> None:
        # kwargs arguments
        self.files = kwargs.get('files')
        self.detach = kwargs.get('detach')

        # Other
        self.torrents = [Torrent(file) for file in self.files]

        self.tasks = []

    def process(self, torrent):

        print(f'Task Executed {threading.current_thread()}')

    def start(self):
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
