import os
import sys
import struct

path = sys.argv[1]

if (os.path.isdir(path)):
    files = os.listdir(path)
    files.sort(key=lambda x: int(x.split('-')[-1]))
else:
    files = [path.split('/')[-1]]
    path = '/'.join(path.split('/')[:-1])

def pretty_print(*args, **kwargs):
    # print(*args, **kwargs)
    for idx, b in enumerate(args[0]):
        if idx % 16 == 0:
            print(f"\n{idx//16:08x}:\t", end="")
        print(f"{b:02x}",end="")
        if (idx + 1) % 2 == 0:
            print(" ", end="")


def parse_file(path):
    print("Seed: ", path)
    buffer = open(path, 'rb').read()
    # print(buffer)
    cnt, = struct.unpack('<Q', buffer[:8])
    cur = 8
    print("Total objects:" , cnt)
    obj_sizes = list(struct.unpack('<' + 'Q' * cnt, buffer[8: 8+8*cnt]))
    cur += 8*cnt
    # print(obj_sizes)
    for idx, i in enumerate(obj_sizes):
        print(f"[OBJ{idx}] ", end="")
        pretty_print(buffer[cur:cur+i])
        print("")
        cur += i
    

for file in files:
    if not file.startswith("id-"):
        continue
    parse_file(os.path.join(path, file))
    print("\n-----------")
