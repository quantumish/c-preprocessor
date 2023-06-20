import codecs
import encodings
from encodings import utf_8
import io

from dataclasses import dataclass
import sys
from collections import namedtuple
import re

a = """
#define TESTING 1

def myfunc():
    return TESTING

#ifdef TESTING
def debug_func():
    print("whee")
    if TESTING:
        print("whoo")
#endif

"""


def handle_define(tokens, state):
    if len(tokens) == 1:
        print("Error: bare #define", file=sys.stderr)
        exit(1)
    if len(tokens) > 2:
        state.defs[tokens[1]] = " ".join(tokens[2:])
    else:
        state.defs[tokens[1]] = ""

def handle_ifdef(tokens, state):
    if len(tokens) == 1:
        print("Error: bare #ifdef", file=sys.stderr)
        exit(1)

    if tokens[1] not in state.defs:
        state.skip = True


def handle_endif(tokens, state):
    skip = False
        
Directive = namedtuple("Directive", "name handler")

handlers = [
    Directive("#define", handle_define),
    # Directive("#ifdef", handle_ifdef),
    Directive("#endif", handle_endif)
    # Directive("#ifndef", handle_ifndef)
]

def try_handle_directive(tokens, state):
    if len(tokens) == 0: return False
    for directive in handlers:
        if tokens[0] == directive.name:
            directive.handler(tokens, state)
            del[state.lines[state.i]]
            return True
    return False

@dataclass
class State:
    defs: dict
    skip: bool
    lines: list
    i: int

    def __init__(self, lines):
        self.defs = {}
        self.skip = False
        self.lines = lines
        self.i = 0

def preprocess(code):
    lines = code.split("\n")
    state = State(lines)
    while state.i < len(lines):
        tokens = re.split("(?<=\S)\s+", state.lines[state.i])

        if len(tokens) == 2 and tokens[0] == "#ifdef":
            handle_ifdef(tokens, state)
            del[state.lines[state.i]]
            continue
        
        for j in range(len(tokens)):
            for definition in state.defs: # GROSS
                tokens[j] = tokens[j].replace(definition, state.defs[definition])                

        if try_handle_directive(tokens, state):
            continue

        if state.skip:
            del state.lines[state.i]
            continue

        state.lines[state.i] = " ".join(tokens)
        state.i += 1

    return "\n".join(lines)

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
                preprocess(buff.decode()).encode(), final=True
            )
        else:
            return ""


class StreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        self.stream = io.StringIO("print('hi')")

        
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
