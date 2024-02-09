solver=KO_USE_THOROUPY
# solver=KO_USE_Z3
export ${solver}=1
export KO_TRACE_BB=1
# export CPPFLAGS="-D UNDERCONSTRAINED=1"
cd ../build && make -j \
  && make  install \
  && cd ../testsuite \
  && KO_WRAP_INDIRECT_CALL=1 METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o global.ll global.c \
  && KO_WRAP_INDIRECT_CALL=1 METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/global global.c \
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
  && METADATA=backlog.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o backlog.ll backlog.c \
  && METADATA=backlog.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/backlog backlog.c \
  && KO_WRAP_INDIRECT_CALL=1 METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o indirect.ll indirect.c \
  && KO_WRAP_INDIRECT_CALL=1 METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/indirect indirect.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o pseudo_pointer.ll pseudo_pointer.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/pp pseudo_pointer.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o container_of.ll container_of.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/co container_of.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o loop.ll loop.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/loop loop.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -S -emit-llvm -o asm.ll asm.c \
  && METADATA=note.yaml KO_CC=clang-12 KO_DONT_OPTIMIZE=1 ../build/bin/ko-clang -g -o binary/asm asm.c \
  && echo "[+]Done"
unset ${solver}
# KO_CC=clang-12 KO_USE_Z3=1 ../build/bin/ko-clang -S -emit-llvm -o linklist-O3.ll -g linklist.c