solver=KO_USE_THOROUPY
# solver=KO_USE_Z3
export ${solver}=1
cd ../build && make -j \
  && make install \
  && cd ../tmp \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o linklist-O0.ll -g linklist.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/linklist linklist.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o external-O0.ll -g external.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/external external.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/array array.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o array-O0.ll -g array.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/malloc malloc.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -S -emit-llvm -o malloc-O0.ll -g malloc.c \
  && METADATA=struct.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o struct.ll struct.c \
  && METADATA=struct.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/struct struct.c \
  && echo "[+]Done"
unset ${solver}
# KO_CC=clang-12 KO_USE_Z3=1 ../build/bin/ko-clang -S -emit-llvm -o linklist-O3.ll -g linklist.c