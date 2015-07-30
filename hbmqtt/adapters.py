# Copyright (c) 2015 Nicolas JOUANIN
#
# See the file license.txt for copying permission.
import asyncio
import io
from websockets.protocol import WebSocketCommonProtocol
from asyncio import StreamReader, StreamWriter


class ReaderAdapter:
    """
    Base class for all network protocol reader adapter.

    Reader adapters are used to adapt read operations on the network depending on the protocol used
    """

    @asyncio.coroutine
    def read(self, n=-1) -> bytes:
        """
        Read up to n bytes. If n is not provided, or set to -1, read until EOF and return all read bytes.
        If the EOF was received and the internal buffer is empty, return an empty bytes object.
        :return: packet read as bytes data
        """


class WriterAdapter:
    """
    Base class for all network protocol writer adapter.

    Writer adapters are used to adapt write operations on the network depending on the protocol used
    """

    def write(self, data):
        """
        write some data to the protocol layer
        """

    @asyncio.coroutine
    def drain(self):
        """
        Let the write buffer of the underlying transport a chance to be flushed.
        """


class WebSocketsReader(ReaderAdapter):
    """
    WebSockets API reader adapter
    This adapter relies on WebSocketCommonProtocol to read from a WebSocket.
    """
    def __init__(self, protocol: WebSocketCommonProtocol):
        self._protocol = protocol
        self._stream = io.BytesIO(b'')

    @asyncio.coroutine
    def read(self, n=-1) -> bytes:
        yield from self._feed_buffer(n)
        return self._stream.read(n)

    @asyncio.coroutine
    def _feed_buffer(self, n=1):
        """
        Feed the data buffer by reading a Websocket message.
        :param n: if given, feed buffer until it contains at least n bytes
        """
        while len(self._stream.getbuffer()) < n:
            message = yield from self._protocol.recv()
            if message is None:
                break
            if not type(message, bytes):
                raise TypeError("message must be bytes")
            self._stream.getbuffer().append(message)


class WebSocketsWriter(WriterAdapter):
    """
    WebSockets API writer adapter
    This adapter relies on WebSocketCommonProtocol to read from a WebSocket.
    """
    def __init__(self, protocol: WebSocketCommonProtocol):
        self._protocol = protocol
        self._stream = io.BytesIO(b'')

    def write(self, data):
        """
        write some data to the protocol layer
        """
        self._stream.write(data)

    @asyncio.coroutine
    def drain(self):
        """
        Let the write buffer of the underlying transport a chance to be flushed.
        """
        yield from self._protocol.send(self._stream.getbuffer())
        self._stream = io.BytesIO(b'')


class StreamProtocolReader(ReaderAdapter):
    """
    Asyncio Streams API protocol adapter
    This adapter relies on StreamReader to read from a TCP socket.
    Because API is very close, this class is trivial
    """
    def __init__(self, reader: StreamReader):
        self._reader = reader

    @asyncio.coroutine
    def read(self, n=-1) -> bytes:
        return (yield from self._reader.read(n))


class StreamWriterAdapter(WriterAdapter):
    """
    Asyncio Streams API protocol adapter
    This adapter relies on StreamWriter to write to a TCP socket.
    Because API is very close, this class is trivial
    """
    def __init__(self, writer: StreamWriter):
        self._writer = writer

    def write(self, data):
        self._writer.write(data)

    @asyncio.coroutine
    def drain(self):
        yield from self._writer.drain()