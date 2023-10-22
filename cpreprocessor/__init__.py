import codecs
import encodings
from encodings import utf_8
import io
import tokenize
from . import process

def encode(input_string):
    print(encoded_bytes)
    out = (input_string+"a").encode()
    return (out, len(out))
    # Encoding logic ...

def decode(encoded_bytes):
    # out = encoded_bytes.decode()+"a"
    out = "print('hi')"
    return (out, len(out))
    # Decoding logic ...

class IncrementalDecoder(utf_8.IncrementalDecoder):
    def decode(self, inp, final=False):
        self.buffer += inp
        if final:
            buff = self.buffer
            self.buffer = b""
            return super(IncrementalDecoder, self,).decode(
                preprocess(buff).encode(), final=True
            )
        else:
            return ""

class StreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = io.StringIO("print('stream_reader')")
        
def custom_search_function(encoding_name):
    # print(encoding_name)
    if encoding_name != "c_preprocessor": return None
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name='c_preprocessor',
        encode = encode,
        decode = decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=utf8.streamreader,
        streamwriter=utf8.streamwriter
    )

codecs.register(custom_search_function)

