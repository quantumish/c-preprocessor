import codecs
import encodings
from encodings import utf_8
import io

import sys
from dataclasses import dataclass
from collections import namedtuple
import tokenize


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
    Directive("#ifdef", handle_ifdef),
    Directive("#endif", handle_endif)
    # Directive("#ifndef", handle_ifndef)
]

def try_handle_directive(tokens, state):
    if len(tokens) == 0: return False
    for directive in handlers:
        if tokens[0] == directive.name:
            directive.handler(tokens, state)
            return True
    return False

@dataclass
class State:
    defs: dict
    skip: bool
    out_tokens: list
    i: int

    def __init__(self, out_tokens):
        self.defs = {}
        self.skip = False
        self.out_tokens = out_tokens
        self.i = 0

def join_tokens(tokens):
    if len(tokens) == 0: return ""
    out = tokens[0].string
    indent = 0
    for i in range(1, len(tokens)):
        if tokens[i].type == tokenize.INDENT:
            indent += 1
            continue
        elif tokens[i].type == tokenize.DEDENT:
            indent -= 1
            continue
        elif ((tokens[i-1].type in (tokenize.NEWLINE, tokenize.DEDENT, tokenize.INDENT))
              and not (tokens[i].type in (tokenize.NEWLINE, tokenize.COMMENT))):
            out += "    "*indent
        if tokens[i-1].type == tokenize.NAME and tokens[i].type == tokenize.NAME:
            out += " "
        out += tokens[i].string
    return out
        
def preprocess(code):
    f = io.BytesIO(code)
    stream = tokenize.tokenize(f.readline)
    
    out_tokens = []
    state = State(out_tokens)
    next(stream)
    for token in stream:
        if state.skip: continue        
        
        if token.type == tokenize.NAME and token.string in state.defs:                
            out_tokens.append(tokenize.TokenInfo(
                type=tokenize.NAME,
                string=state.defs[token.string],
                start=None, end=None, line=None
            ))
        elif token.type == tokenize.COMMENT:
            dir_tokens = token.string.split()
            try_handle_directive(dir_tokens, state)
        else:
            out_tokens.append(token)

            
    return join_tokens(out_tokens)


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

