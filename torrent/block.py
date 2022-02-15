from enum import Enum


class State(Enum):
    EMPTY = 0
    FULL = 2
    PENDING = 1


class Block:
    SIZE = 2 ** 14

    def __init__(self, state=State.EMPTY, size=None, data=b'', last_send_to_peer=0):
        if not size:
            self.size = self.SIZE
        else:
            self.size = size

        self.state = state
        self.data = data
        self.last_send_to_peer = last_send_to_peer

    def __str__(self):
        return f'{self.state} - {self.size} - {len(self.data)} - {self.last_send_to_peer}'
