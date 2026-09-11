# Isolated C++ measurement headers

The `include/atcoder/` tree is AtCoder Library v1.6 at commit
`864245a00b00dd008d1abfdc239618fdb7d139da`, distributed under CC0. The pinned
Clang container reads it only as a compilation dependency; header bodies remain
outside the measured target-source scope.

`include/utils/debug.h` is an empty compatibility header. One benchmark source
includes that file only when `_DEBUG` is defined. The AST wrapper moves include
directives ahead of its private namespace, so it must be resolvable even though
the measurement build does not define `_DEBUG` and executes no debug code.
