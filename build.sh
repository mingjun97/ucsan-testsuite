cd ../build && make -j \
  && make install \
  && cd ../tmp \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/linklist linklist.c \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o linklist-O0.ll -g linklist.c \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/array array.c \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o array-O0.ll -g array.c \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/malloc malloc.c \
  && KO_CC=clang-12 KO_USE_Z3=1 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o malloc-O0.ll -g malloc.c \
  && echo "[+]Done"
# KO_CC=clang-12 KO_USE_Z3=1 ../build/bin/ko-clang -S -emit-llvm -o linklist-O3.ll -g linklist.c