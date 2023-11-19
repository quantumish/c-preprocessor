# c-preprocessor

Ever felt like your Python code wasn't hacky enough? 
Lamented the bygone `#ifdef`s and cursed macro trickery? This is the Python package for you!

Just by simply adding a single comment to the top of your file, you too can use a crude approximation of the C preprocessor from Python.
```py
# coding: c-prepocessor

#define TESTING 1
#define DOUBLE(x) (x*2)
#define MAX(x,y) x if x > y else y
#define BLAH lots of words

def myfunc():
    return TESTING

#ifdef TESTING
def debug_func():
    print("whee")
    print(DOUBLE(2))
    print(MAX(1, 2), __COUNTER__)
    if TESTING:
         print("whoo")
    print("hah")

debug_func()
#endif
```
Running this yields 
```
whee
4
2 0
whoo
hah
```

`c-preprocessor` has support for the `#define`, `#ifdef`, `#endif`, `#ifndef`, `#include`, `#undef`, and `#else` directives as of now.
Furthermore, the following special preprocessor macros are implemented: 
- `__COUNTER__`: results in a higher number each time it is expanded
- `__VERSION__`, `__PYTHON__`, `__PYTHON_MINOR__`, `__PYTHON_MICRO__`: Python version info
- `__IMPLEMENTATION__`: the Python implementation
- `__FILE_NAME__`
- `__BYTE_ORDER__`, `__ORDER_LITTLE_ENDIAN__`, `__ORDER_BIG_ENDIAN__`: endianness info

# install 
There's not really a proper install process yet. You're gonna want to make a corresponding `.pth` file and install the package as normal.

# how? 
Python supports arbitrary file encodings which are implemented via Python code. This uses that interface to effectively reparse your code at runtime before it starts being evaluated.
This is actually used by Dropbox to do inline HTML: see [here](https://github.com/dropbox/pyxl). 
