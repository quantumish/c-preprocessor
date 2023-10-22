from cpreprocessor import preprocess
import tokenize
import io

def clean_token(token):
    return tokenize.TokenInfo(
        type=token.type,
        string=token.string,
        start=None, end=None, line=None,
    )

def dedent(tokens):
    """Decrease indentation of token list by 1 (in-place)."""
    for i in range(len(tokens)):
        if tokens[i].type == tokenize.INDENT:
            del(tokens[i])
            break
    for i in range(1,len(tokens)-1):
        if tokens[-i].type == tokenize.DEDENT:
            del(tokens[-i])
            break    

def relevant_token(token):
    return (token.type != tokenize.NEWLINE and
            token.type != tokenize.NL and
            token.type != tokenize.ENCODING and
            token.type != tokenize.ENDMARKER)            

def lexically_equiv(a, b):
    a_stream = tokenize.tokenize(io.BytesIO(bytes(a, "utf8")).readline)
    b_stream = tokenize.tokenize(io.BytesIO(bytes(b, "utf8")).readline)

    a_toks = list(map(clean_token, filter(relevant_token, a_stream)))
    b_toks = list(map(clean_token, filter(relevant_token, b_stream)))    
    dedent(a_toks)
    dedent(b_toks)
    
    print(a_toks)
    print(b_toks)
        
    return a_toks == b_toks

def test_sanity():
    assert(lexically_equiv(
        preprocess(b"print(1+1)"), "print(1+1)"
    ))

def test_ifdef():
    code = b"""
    #define TESTING

    #ifdef TESTING
    print(1+1)
    #endif
    """
    
    assert(lexically_equiv(preprocess(code), "print(1+1)"))

    code = b"""
    #ifdef TESTING
    print(1+1)
    #endif
    """
    assert(lexically_equiv(preprocess(code), ""))

    
    
    
