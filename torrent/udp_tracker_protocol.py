import random
import socket
from struct import pack, unpack

from torrent.exception import IsNotInitialized


class UDPTrackerProtocolInterface:
    ZERO = 0

    def __init__(self) -> None:
        pass

    def to_bytes(self) -> None:
        raise NotImplementedError()

    def from_bytes(self, payload) -> None:
        raise NotImplementedError()


class ConnectionRequest(UDPTrackerProtocolInterface):
    """ connect request:

        Offset  Size            Name            Value
        0       64-bit integer  protocol_id     0x41727101980 // magic constant
        8       32-bit integer  action          0 // connect
        12      32-bit integer  transaction_id
        16

        1. Receive the packet.
        2. Check whether the packet is at least 16 bytes.
        3. Check whether the transaction ID is equal to the one you chose.
        4. Check whether the action is connect.
        5. Store the connection ID for future use.

        TODO: Check if order mixed up. Should be action, transaction_id, connection_id (protocol_id)?
    """
    TOTAL_LENGTH = 64 + 32 + 32
    PROTOCOL_ID = 0x41727101980

    def __init__(self) -> None:
        super().__init__()

        self.connection_id = self.PROTOCOL_ID
        self.action = self.ZERO
        self.transaction_id = random.randint(self.ZERO, 100000)

    def to_bytes(self) -> bytes:
        connection_id = pack('>Q', self.connection_id)
        action = pack('>I', self.action)
        transaction_id = pack('>I', self.transaction_id)

        return connection_id + action + transaction_id

    def from_bytes(self, payload) -> None:
        self.connection_id, = unpack('>Q', payload[:8])
        self.action, = unpack('>I', payload[8:12])
        self.transaction_id, = unpack('>I', payload[12:16])


class ConnectionResponse(UDPTrackerProtocolInterface):
    """ connect response:

        Offset  Size            Name            Value
        0       32-bit integer  action          0 // connect
        4       32-bit integer  transaction_id
        8       64-bit integer  connection_id
        16
    """
    def __init__(self):
        super().__init__()

        self.action = self.ZERO
        self.transaction_id = random.randint(self.ZERO, 100000)
        self.connection_id = None

    def to_bytes(self) -> bytes:
        if not self.connection_id:
            raise IsNotInitialized('ConnectionResponse is not initialized')

        action = pack('>I', self.action)
        transaction_id = pack('>I', self.transaction_id)
        connection_id = pack('>Q', self.connection_id)

        return action + transaction_id + connection_id

    def from_bytes(self, payload) -> None:
        self.action, = unpack('>I', payload[:4])
        self.transaction_id, = unpack('>I', payload[4:8])
        self.connection_id, = unpack('>I', payload[8:16])


class IPv4AnnounceRequest(UDPTrackerProtocolInterface):
    """ IPv4 announce request:

        Offset  Size    Name    Value
        0       64-bit integer  connection_id
        8       32-bit integer  action          1 // announce
        12      32-bit integer  transaction_id
        16      20-byte string  info_hash
        36      20-byte string  peer_id
        56      64-bit integer  downloaded
        64      64-bit integer  left
        72      64-bit integer  uploaded
        80      32-bit integer  event           0 // 0: none; 1: completed; 2: started; 3: stopped
        84      32-bit integer  IP address      0 // default
        88      32-bit integer  key
        92      32-bit integer  num_want        -1 // default
        96      16-bit integer  port
        98

        1. Receive the packet.
        2. Check whether the packet is at least 20 bytes.
        3. Check whether the transaction ID is equal to the one you chose.
        4. Check whether the action is announce.
        5. Do not announce again until interval seconds have passed or an event has occurred.
    """
    TOTAL_LENGTH = 64 + 32 + 32

    def __init__(self, info_hash, connection_id, peer_id) -> None:
        """ TODO: Move to from_bytes
        """
        super().__init__()

        self.action = 1
        self.connection_id = connection_id
        self.peer_id = peer_id
        self.info_hash = info_hash
        self.transaction_id = random.randint(self.ZERO, 100000)

    def to_bytes(self) -> bytes:
        connection_id = pack('>Q', self.connection_id)
        action = pack('>I', self.action)
        transaction_id = pack('>I', self.transaction_id)
        downloaded = pack('>Q', self.ZERO)
        left = pack('>Q', self.ZERO)
        uploaded = pack('>Q', self.ZERO)

        event = pack('>I', self.ZERO)
        ip = pack('>I', self.ZERO)
        key = pack('>I', self.ZERO)
        num_want = pack('>i', -1)
        port = pack('>h', 8000)

        msg = (connection_id + action + transaction_id +
               self.info_hash + self.peer_id +
               downloaded + left + uploaded + event +
               ip + key + num_want + port)

        return msg

    def from_bytes(self, payload) -> None:
        raise NotImplementedError()


class IPv4AnnounceResponse(UDPTrackerProtocolInterface):
    """ IPv4 announce response:

        Offset      Size            Name            Value
        0           32-bit integer  action          1 // announce
        4           32-bit integer  transaction_id
        8           32-bit integer  interval
        12          32-bit integer  leechers
        16          32-bit integer  seeders
        20 + 6 * n  32-bit integer  IP address
        24 + 6 * n  16-bit integer  TCP port
        20 + 6 * N
    """
    def __init__(self) -> None:
        super().__init__()

        self.action = 1
        self.transaction_id = None
        self.interval = None
        self.leechers = None
        self.seeders = None
        self.socket_addresses = []

    def to_bytes(self) -> bytes:
        """ TODO: unpack socket_addresses
        """
        if not self.transaction_id:
            raise IsNotInitialized('IPv4AnnounceResponse is not initialized')

        action, = unpack('>I', self.action)
        transaction_id, = unpack('>I', self.transaction_id)
        interval, = unpack('>I', self.interval)
        leechers, = unpack('>I', self.leechers)
        seeders, = unpack('>I', self.seeders)
        socket_addresses = b'00000000'

        return action + transaction_id + interval + leechers + seeders + socket_addresses

    def from_bytes(self, payload) -> None:
        self.action, = unpack('>I', payload[:4])
        self.transaction_id, = unpack('>I', payload[4:8])
        self.interval, = unpack('>I', payload[8:12])
        self.leechers, = unpack('>I', payload[12:16])
        self.seeders, = unpack('>I', payload[16:20])
        self.socket_addresses = payload

    @property
    def socket_addresses(self) -> list:
        return self.__socket_addresses

    @socket_addresses.setter
    def socket_addresses(self, payload) -> None:
        raw_bytes = payload[20:]
        addresses = []
        addresses_length = int(len(raw_bytes) / 6)

        for i in range(addresses_length):
            _start_byte = i * 6
            _end_byte = _start_byte + 6

            ip = socket.inet_ntoa(raw_bytes[_start_byte:(_end_byte - 2)])
            raw_port = raw_bytes[(_end_byte - 2):_end_byte]
            port = raw_port[1] + raw_port[self.ZERO] * 256

            addresses.append((ip, port))

        self.__socket_addresses = addresses


class ScrapeRequest(UDPTrackerProtocolInterface):
    """ scrape request:

        Offset          Size            Name            Value
        0               64-bit integer  connection_id
        8               32-bit integer  action          2 // scrape
        12              32-bit integer  transaction_id
        16 + 20 * n     20-byte string  info_hash
        16 + 20 * N

        1. Receive the packet.
        2. Check whether the packet is at least 8 bytes.
        3. Check whether the transaction ID is equal to the one you chose.
        4. Check whether the action is scrape.
    """
    def __init__(self) -> None:
        super().__init__()

        self.connection_id = None
        self.action = 2
        self.transaction_id = random.randint(self.ZERO, 100000)
        self.info_hash = None

    def to_bytes(self) -> bytes:
        connection_id = pack('>Q', self.connection_id)
        action = pack('>I', self.action)
        transaction_id = pack('>I', self.transaction_id)

        return connection_id + action + transaction_id + self.info_hash

    def from_bytes(self, payload) -> None:
        self.connection_id, = unpack('>Q', payload[:8])
        self.action, = unpack('>I', payload[8:12])
        self.transaction_id, = unpack('>I', payload[12:16])
        # TODO: set info_hash


class ScrapeResponse(UDPTrackerProtocolInterface):
    """ scrape response:

        Offset      Size            Name            Value
        0           32-bit integer  action          2 // scrape
        4           32-bit integer  transaction_id
        8 + 12 * n  32-bit integer  seeders
        12 + 12 * n 32-bit integer  completed
        16 + 12 * n 32-bit integer  leechers
        8 + 12 * N

        If the tracker encounters an error, it might send an error packet.

            1. Receive the packet.
            2. Check whether the packet is at least 8 bytes.
            3. Check whether the transaction ID is equal to the one you chose.
    """
    def __init__(self, payload):
        super().__init__()

        self.action = 2
        self.seeders = None
        self.connection_id = None

    def to_bytes(self) -> bytes:
        if not self.connection_id:
            raise IsNotInitialized('ScrapeResponse is not initialized')

        action = pack('>I', self.action)
        seeders = pack('>I', self.seeders)
        connection_id = pack('>Q', self.connection_id)

        return action + seeders + connection_id

    def from_bytes(self, payload) -> None:
        self.action, = unpack('>I', payload[:4])
        self.seeders, = unpack('>I', payload[4:8])
        self.connection_id, = unpack('>Q', payload[8: 16])


class ErrorResponse(UDPTrackerProtocolInterface):
    """ error response:

        Offset  Size            Name            Value
        0       32-bit integer  action          3 // error
        4       32-bit integer  transaction_id
        8       string  message
    """
    def __init__(self):
        super().__init__()

        self.action = 3
        self.transaction_id = None
        self.message = None

    def to_bytes(self) -> bytes:
        if not self.transaction_id:
            raise IsNotInitialized('ErrorResponse is not initialized')

        _bytes_message = bytes(self.message, 'utf-8')
        _message_length = len(_bytes_message)

        action = pack('>I', self.action)
        transaction_id = pack('>I', self.transaction_id)
        message = pack(f'>{_message_length}s', _bytes_message)

        return action + transaction_id + message

    def from_bytes(self, payload) -> None:
        _message_length = len(self.message)

        self.action, = unpack('>I', payload[:4])
        self.transaction_id, = unpack('>I', payload[4:8])
        self.message, = unpack(f'>{_message_length}s', payload[8:])
