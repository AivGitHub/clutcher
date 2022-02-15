from struct import pack, unpack

import bitstring

from torrent.exception import WrongMessageException


class MessageInterface:
    """ Mixin for BitTorrent Messages protocol

    """
    HANDSHAKE_PSTR_V1 = b'BitTorrent protocol'
    HANDSHAKE_PSTR_LEN = len(HANDSHAKE_PSTR_V1)
    LENGTH_PREFIX = 4
    BLOCK_LENGTH_PREFIX = 9
    ZERO = 0

    def __init__(self):
        pass

    def to_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, payload):
        raise NotImplementedError()

    def get_class_name(self):
        return type(self).__name__


class Handshake(MessageInterface):
    """ handshake: <pstrlen><pstr><reserved><info_hash><peer_id>

        The handshake is a required message and must be the first message transmitted by the client.
        It is (49+len(pstr)) bytes long.

            - pstrlen: string length of <pstr>, as a single raw byte
            - pstr: string identifier of the protocol
            - reserved: eight (8) reserved bytes. All current implementations use all zeroes.
              Each bit in these bytes can be used to change the behavior of the protocol.
              An email from Bram suggests that trailing bits should be used first,
              so that leading bits may be used to change the meaning of trailing bits.
            - info_hash: 20-byte SHA1 hash of the info key in the metainfo file.
              This is the same info_hash that is transmitted in tracker requests.
            - peer_id: 20-byte string used as a unique ID for the client.
    """
    PAYLOAD_LENGTH = 49 + 19
    TOTAL_LENGTH = 49 + 19

    def __init__(self, info_hash, peer_id=b'-CL0001-000000000000'):
        super().__init__()

        assert len(info_hash) == 20
        assert len(peer_id) < 255
        self.peer_id = peer_id
        self.info_hash = info_hash

    def to_bytes(self):
        reserved = b'\x00' * 8
        handshake = pack(f'>B{self.HANDSHAKE_PSTR_LEN}s8s20s20s',
                         self.HANDSHAKE_PSTR_LEN,
                         self.HANDSHAKE_PSTR_V1,
                         reserved,
                         self.info_hash,
                         self.peer_id)

        return handshake

    @classmethod
    def from_bytes(cls, payload):
        pstrlen, = unpack('>B', payload[:1])
        pstr, reserved, info_hash, peer_id = unpack(f'>{pstrlen}s8s20s20s', payload[1:cls.TOTAL_LENGTH])

        if pstr != cls.HANDSHAKE_PSTR_V1:
            raise ValueError('Invalid protocol identifier')

        return Handshake(info_hash, peer_id)


class KeepAlive(MessageInterface):
    """ keep-alive: <len=0000>

        The keep-alive message is a message with zero bytes, specified with the length prefix set to zero.
        There is no message ID and no payload. Peers may close a connection if they receive
        no messages (keep-alive or any other message) for a certain period of time, so a keep-alive message
        must be sent to maintain the connection alive if no command have been sent for a
        given amount of time.
    """
    ID = None

    PAYLOAD_LENGTH = MessageInterface.ZERO
    TOTAL_LENGTH = 4

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack('>I', self.PAYLOAD_LENGTH)

    @classmethod
    def from_bytes(cls, payload):
        payload_length = unpack('>I', payload[:cls.TOTAL_LENGTH])

        if payload_length != cls.ZERO:
            raise WrongMessageException('Not a Keep Alive message')

        return KeepAlive()


class Choke(MessageInterface):
    """ choke: <len=0001><id=0>

        The choke message is fixed-length and has no payload.
    """
    ID = MessageInterface.ZERO

    PAYLOAD_LENGTH = 1
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack('>IB', self.PAYLOAD_LENGTH, self.ID)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id = unpack('>IB', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not a Choke message')

        return Choke()


class UnChoke(MessageInterface):
    """ unchoke: <len=0001><id=1>

        The unchoke message is fixed-length and has no payload.
    """
    ID = 1

    PAYLOAD_LENGTH = 1
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack('>IB', self.PAYLOAD_LENGTH, self.ID)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id = unpack('>IB', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not an UnChoke message')

        return UnChoke()


class Interested(MessageInterface):
    """ interested: <len=0001><id=2>

        The interested message is fixed-length and has no payload.
    """
    ID = 2

    PAYLOAD_LENGTH = 1
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack('>IB', self.PAYLOAD_LENGTH, self.ID)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id = unpack('>IB', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not an Interested message')

        return Interested()


class NotInterested(MessageInterface):
    """ not interested: <len=0001><id=3>

        The not interested message is fixed-length and has no payload.
    """
    ID = 3

    PAYLOAD_LENGTH = 1
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack('>IB', self.PAYLOAD_LENGTH, self.ID)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack('>IB', payload[:cls.TOTAL_LENGTH])

        if message_id != cls.ID:
            raise WrongMessageException('Not a NotInterested message')

        return NotInterested()


class Have(MessageInterface):
    """ have: <len=0005><id=4><piece index>

        The have message is fixed length.
        The payload is the zero-based index of a piece that has
        just been successfully downloaded and verified via the hash.
    """
    ID = 4

    PAYLOAD_LENGTH = 5
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self, piece_index):
        super().__init__()
        self.piece_index = piece_index

    def to_bytes(self):
        pack('>IBI', self.PAYLOAD_LENGTH, self.ID, self.piece_index)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id, piece_index = unpack('>IBI', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not a Have message')

        return Have(piece_index)


class BitField(MessageInterface):
    """ bitfield: <len=0001+X><id=5><bitfield>

        The bitfield message may only be sent immediately after the handshaking sequence is completed,
        and before any other messages are sent. It is optional, and need not be sent if a client has no pieces.

        The bitfield message is variable length, where X is the length of the bitfield.
        The payload is a bitfield representing the pieces that have been successfully downloaded.
        The high bit in the first byte corresponds to piece index 0.
        Bits that are cleared indicated a missing piece, and set bits indicate a valid and available piece.
        Spare bits at the end are set to zero.

        Some clients (Deluge for example) send bitfield with missing pieces even if it has all data.
        Then it sends rest of pieces as have messages.
        They are saying this helps against ISP filtering of BitTorrent protocol. It is called lazy bitfield.

        A bitfield of the wrong length is considered an error.
        Clients should drop the connection if they receive bitfields that are not of the correct size,
        or if the bitfield has any of the spare bits set.
    """
    ID = 5

    # Unknown
    PAYLOAD_LENGTH = -1
    TOTAL_LENGTH = -1

    def __init__(self, bitfield: bitstring.BitArray):
        super().__init__()

        self.bitfield = bitfield
        self.bitfield_as_bytes = bitfield.tobytes()
        self.bitfield_length = len(self.bitfield_as_bytes)

        self.PAYLOAD_LENGTH = 1 + self.bitfield_length
        self.TOTAL_LENGTH = self.LENGTH_PREFIX + self.PAYLOAD_LENGTH

    def to_bytes(self):
        return pack(f'>IB{self.bitfield_length}s',
                    self.PAYLOAD_LENGTH,
                    self.ID,
                    self.bitfield_as_bytes)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id = unpack('>IB', payload[:5])
        bitfield_length = payload_length - 1

        if _id != cls.ID:
            raise WrongMessageException('Not a BitField message')

        raw_bitfield, = unpack(f'>{bitfield_length}s', payload[5:5 + bitfield_length])
        bitfield = bitstring.BitArray(bytes=bytes(raw_bitfield))

        return BitField(bitfield)


class Request(MessageInterface):
    """ request: <len=0013><id=6><index><begin><length>

        The request message is fixed length, and is used to request a block.
        The payload contains the following information:

            - index: integer specifying the zero-based piece index
            - begin: integer specifying the zero-based byte offset within the piece
            - length: integer specifying the requested length.
    """
    ID = 6

    PAYLOAD_LENGTH = 13
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self, piece_index, block_offset, block_length):
        super().__init__()

        self.piece_index = piece_index
        self.block_offset = block_offset
        self.block_length = block_length

    def to_bytes(self):
        return pack('>IBIII',
                    self.PAYLOAD_LENGTH,
                    self.ID,
                    self.piece_index,
                    self.block_offset,
                    self.block_length)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id, piece_index, block_offset, block_length = unpack('>IBIII', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not a Request message')

        return Request(piece_index, block_offset, block_length)


class Piece(MessageInterface):
    """ piece: <len=0009+X><id=7><index><begin><block>

        The piece message is variable length, where X is the length of the block.
        The payload contains the following information:

            - index: integer specifying the zero-based piece index
            - begin: integer specifying the zero-based byte offset within the piece
            - block: block of data, which is a subset of the piece specified by index.
    """
    ID = 7

    # Unknown
    PAYLOAD_LENGTH = -1
    TOTAL_LENGTH = -1

    def __init__(self, block_length, piece_index, block_offset, block):
        super().__init__()

        self.block_length = block_length
        self.piece_index = piece_index
        self.block_offset = block_offset
        self.block = block

        self.PAYLOAD_LENGTH = self.BLOCK_LENGTH_PREFIX + block_length
        self.TOTAL_LENGTH = self.LENGTH_PREFIX + self.PAYLOAD_LENGTH

    def to_bytes(self):
        return pack(f'>IBII{self.block_length}s',
                    self.PAYLOAD_LENGTH,
                    self.ID,
                    self.piece_index,
                    self.block_offset,
                    self.block)

    @classmethod
    def from_bytes(cls, payload):
        block_length = len(payload) - 13
        payload_length, _id, piece_index, block_offset, block = unpack(f'>IBII{block_length}s',
                                                                       payload[:13 + block_length])

        if _id != cls.ID:
            raise WrongMessageException('Not a Piece message')

        return Piece(block_length, piece_index, block_offset, block)


class Cancel(MessageInterface):
    """ cancel: <len=0013><id=8><index><begin><length>

        The cancel message is fixed length, and is used to cancel block requests.
        The payload is identical to that of the "request" message.
        It is typically used during "End Game".
    """
    ID = 8
    PAYLOAD_LENGTH = 13
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self, piece_index, block_offset, block_length):
        super(Cancel, self).__init__()

        self.piece_index = piece_index
        self.block_offset = block_offset
        self.block_length = block_length

    def to_bytes(self):
        return pack('>IBIII',
                    self.PAYLOAD_LENGTH,
                    self.ID,
                    self.piece_index,
                    self.block_offset,
                    self.block_length)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id, piece_index, block_offset, block_length = unpack('>IBIII', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not a Cancel message')

        return Cancel(piece_index, block_offset, block_length)


class Port(MessageInterface):
    """ port: <len=0003><id=9><listen-port>

        The port message is sent by newer versions of the Mainline that implements a DHT tracker.
        The listen port is the port this peer's DHT node is listening on.
        This peer should be inserted in the local routing table (if DHT tracker is supported).
    """
    ID = 9

    PAYLOAD_LENGTH = 5
    TOTAL_LENGTH = MessageInterface.LENGTH_PREFIX + PAYLOAD_LENGTH

    def __init__(self, port):
        super().__init__()

        self.port = port

    def to_bytes(self):
        return pack('>IBI',
                    self.PAYLOAD_LENGTH,
                    self.ID,
                    self.port)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, _id, port = unpack('>IBI', payload[:cls.TOTAL_LENGTH])

        if _id != cls.ID:
            raise WrongMessageException('Not a Port message')

        return Port(port)


class Dispatcher:
    MESSAGES_MAPPED = {
        0: Choke,
        1: UnChoke,
        2: Interested,
        3: NotInterested,
        4: Have,
        5: BitField,
        6: Request,
        7: Piece,
        8: Cancel,
        9: Port
    }

    def __init__(self, payload):
        self.payload = payload

    def dispatch(self):
        payload_length, _id, = unpack('>IB', self.payload[:5])
        message = self.MESSAGES_MAPPED.get(_id)

        if message:
            return message.from_bytes(self.payload)

        raise WrongMessageException(f'Wrong message id: {_id}')
