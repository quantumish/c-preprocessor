import codecs
import encodings
from encodings import utf_8
import io

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
        if inp != b"":
            # NOTE: buffer MUST start with '\n'
            self.buffer += b'\nprint("hi")'
        if final:
            buff = self.buffer
            self.buffer = b""
            return super(IncrementalDecoder, self,).decode(
                buff, final=True
            )
        else:
            return ""


class StreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = io.StringIO("print('hi')")

        
def custom_search_function(encoding_name):
    if encoding_name != "cprepross": return None
    utf8=encodings.search_function('utf8')
    return codecs.CodecInfo(
        name='cprepross',
        encode = encode,
        decode = decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=utf8.streamreader,
        streamwriter=utf8.streamwriter
    )

codecs.register(custom_search_function)
