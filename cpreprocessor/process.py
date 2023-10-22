import sys
import re
from dataclasses import dataclass
from collections import namedtuple
import tokenize

Macro = namedtuple("Macro", "args func")

def check_bare(tokens, directive_name):
    if len(tokens) == 1:
        print(f"Error: bare {directive_name}", file=sys.stderr)
        exit(1)

def handle_define(tokens, state):
    check_bare(tokens, "#define")
    if len(tokens) > 2:
        if (m := re.search('\((.*?)\)', tokens[1])):
            content = " ".join(tokens[2:])
            args = m.group(0)[1:-1].split(",")

            def macro(inps):
                copy = content
                for (i, inp) in enumerate(inps):
                    copy = copy.replace(args[i], inp)
                return copy
                    
            state.defs[tokens[1][:m.span()[0]]] = Macro(
                len(args),
                macro
            )
            
        else:
            state.defs[tokens[1]] = " ".join(tokens[2:])
    else:        
        state.defs[tokens[1]] = ""

def handle_undef(tokens, state):
    check_bare(tokens, "#undef")
    try:
        state.defs.pop(tokens[1])
    except:
        pass
    
def handle_ifdef(tokens, state):
    check_bare(tokens, "#ifdef")
    if tokens[1] not in state.defs:
        state.skip = True
        state.prev_cond = False
    else:
        state.prev_cond = True

def handle_ifndef(tokens, state):
    check_bare(tokens, "#ifndef")
    if tokens[1] in state.defs:
        state.skip = True
        state.prev_cond = True
    else:
        state.prev_cond = False

def handle_include(tokens, state):
    check_bare(tokens, "#include")

    if (m := re.search('"(.*?)"', tokens[1])):
        f = open(m.group(0)[1:-1], "rb")
        stream = tokenize.tokenize(f.readline)
        next(stream)
        for tok in stream:
            state.out_tokens.append(tok)
    elif (fname := re.search('<(.*?)>', tokens[1])):
        print("Error: PYTHON_PATH handling not implemented. Also why would you do this.")
        exit(1)
    else:
        print("Error: malformed #include", file=sys.stderr)
        exit(1)
        
def handle_endif(tokens, state):
    if state.prev_cond is None:
        print("Error: #endif without #if", file=sys.stderr)
        exit(1)
    if state.skip:        
        state.skip = False
    state.prev_cond = None

def handle_else(tokens, state):
    if state.prev_cond is None:
        print("Error: #else without #if", file=sys.stderr)
        exit(1)
    elif state.prev_cond == True:
        state.skip=True
        
Directive = namedtuple("Directive", "name handler")

handlers = [
    Directive("#define", handle_define),
    Directive("#ifdef", handle_ifdef),
    Directive("#endif", handle_endif),
    Directive("#ifndef", handle_ifndef),
    Directive("#include", handle_include),
    Directive("#undef", handle_undef),
    Directive("#else", handle_else),
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
    prev_cond: bool
    out_tokens: list
    i: int

    def __init__(self, out_tokens):
        self.defs = {
            "__COUNTER__": "0", # TODO refactor macro expansion into its own function
            "__VERSION__": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "__PYTHON__": str(sys.version_info.major),
            "__PYTHON_MINOR__": str(sys.version_info.minor),
            "__PYTHON_MICRO__": str(sys.version_info.micro),
            "__IMPLEMENTATION__": sys.implementation.name,
            "__FILE_NAME__": __file__,
            "__BYTE_ORDER__": sys.byteorder,
            "__ORDER_LITTLE_ENDIAN__": "little",
            "__ORDER_BIG_ENDIAN__": "big",
            # TODO __TIMESTAMP__ (last modified of exec'd file)
        }
        if sys.flags.optimize:
            self.defs["__OPTIMIZE__"] = str(sys.flags.optimize)
        if sys.platform == "linux":
            self.defs["__linux__"] = "1"
        if sys.platform == "darwin":
            self.defs["__APPLE__"] = "1"        
            
        self.skip = False
        self.prev_cond = None
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
    macro_call = None
    for token in stream:
        if state.skip: continue
        
        if token.type == tokenize.NAME and token.string in state.defs:
            if isinstance(state.defs[token.string], Macro):
                macro_call = state.defs[token.string]
                lparen = next(stream)
                inps = []
                for i in range(macro_call.args):
                    val = next(stream)
                    if (val.string == ","): val = next(stream)
                    inps.append(val.string)                    
                rparen = next(stream)
                print(inps, rparen)
                if lparen.string != "(" or rparen.string != ")":
                    print("Invalid macro call!", file=sys.stderr)                    
                    exit(1)
                out_tokens.append(tokenize.TokenInfo(
                    type = tokenize.NAME, # HACK
                    string = state.defs[token.string].func(inps),
                    start=None, end=None, line=None
                ))
            else:
                out_tokens.append(tokenize.TokenInfo(
                    type=tokenize.NAME,
                    string=state.defs[token.string],
                    start=None, end=None, line=None
                ))
                if token.string == "__COUNTER__":
                    state.defs["__COUNTER__"] = str(int(state.defs["__COUNTER__"]) + 1)
        elif token.type == tokenize.COMMENT:
            dir_tokens = token.string.split()
            try_handle_directive(dir_tokens, state)
        else:
            out_tokens.append(token)
        
    return join_tokens(out_tokens)
