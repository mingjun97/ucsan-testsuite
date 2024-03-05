import json
import yaml
import os
import subprocess
from tqdm.contrib.concurrent import process_map
from multiprocessing import Manager
import threading
import time
import sys

KO_FLAGS = ["KO_USE_THOROUPY=1", "KO_TRACE_BB=1", "KO_CC=clang-12", 
            "KO_DONT_OPTIMIZE=1",
            "KO_WRAP_INDIRECT_CALL=1", "KO_UCSAN=1", 
            "KO_CHECKER_UBI=1", "KO_RESIGN_PTRARGS=1"]

KO_FLAGS.remove("KO_CHECKER_UBI=1") # disable ubi checker

ko_flags = ' '.join(KO_FLAGS)
# cc = "opt-12 -load /mnt/shared/ucsan/build/lib/symsan/libTaintPass.so" \
#      " -taint-abilist=/mnt/shared/ucsan/build/lib/symsan/dfsan_abilist.txt" \
#      " -taint-abilist=/mnt/shared/ucsan/build/lib/symsan/zlib_abilist.txt"  \
#      " -O0 -S -disable-verify"
cc = "opt-12 -load /mnt/shared/ucsan/build/lib/symsan/libTaintPass.so" \
     " -O0 -S -disable-verify"
ko_cc = "/mnt/shared/ucsan/build/bin/ko-clang"
dest_dir = "/mnt/shared/binaries"
write_to_file = True
write_to = "errors_mp.json"
if len(sys.argv) > 2:
    dest_dir = "./" # redirect to current folder as it's a debug build
    write_to_file = False


manager = Manager()
queue = manager.Queue()

class ColorPrint:
    def __init__(self, color):
        self.color = {
            "blue": 94,
            "cyan": 96,
            "green": 92,
            "yellow": 93,
            "fail": 91,
            "underline": 4,
        }[color.lower()]
    def __enter__(self):
        print(f"\033[{self.color}m", end='')
    def __exit__(self, *args):
        print("\033[0m", end='')

def execute(command):
    # with ColorPrint("yellow"):
    #     print(f"{command}")
    # return 0
    # return os.system(command)
    if write_to_file == False:
        print(command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return *p.communicate(), p.returncode

def compile(idx, tp: dict, fn:str = "tmp.ll"):
    # global errors, success, len_all
    # len_all += 1
    path = tp['_path']
    yaml.dump({"entry": tp['entry'], "scope": tp.get('scope', [])}, open(f"ko-{fn}.yaml", "w"))
    
    # execute(f"rm -f {path}.o")
    # execute(f"rm -f {path}.ll")
    stdout, stderr, ret = execute(f"{ko_flags}  METADATA={os.curdir}/ko-{fn}.yaml {cc} {path} -o {fn}")
    files = [f"{fn}.o"]
    if ret != 0:
        # with ColorPrint("fail"):
        #     print(f"{path} failed at compile stage")
        return ('p1', {
            'stdout': stdout.decode('latin2'),
            'stderr': stderr.decode('latin2'),
            'data': tp
        })
    
    stdout, stderr, ret = execute(f"llc-12 -filetype=obj --relocation-model=pic -o {fn}.o {fn}")
    if ret != 0:
        # with ColorPrint("fail"):
        #     print(f"{path} failed at compile stage(2)")
            return ('p2', {
                'stdout': stdout.decode('latin2'),
                'stderr': stderr.decode('latin2'),
                'data': tp
            })
    
    for dep_idx, deps in enumerate(tp.get('objs', [])):
        stdout, stderr, ret = execute(f"{ko_flags}  METADATA={os.curdir}/ko-{fn}.yaml NOT_ENTRY_OBJECT=1 {cc} {deps} -o {fn}.{dep_idx}")
        files.append(f"{fn}.{dep_idx}.o")
        if ret != 0:
            # with ColorPrint("fail"):
            #     print(f"{path} failed at compile stage")
            return ('p1', {
                'stdout': stdout.decode('latin2'),
                'stderr': stderr.decode('latin2'),
                'data': tp
            })
        
        stdout, stderr, ret = execute(f"llc-12 -filetype=obj --relocation-model=pic -o {fn}.{dep_idx}.o {fn}.{dep_idx}")
        if ret != 0:
            # with ColorPrint("fail"):
            #     print(f"{path} failed at compile stage(2)")
            return ('p2', {
                'stdout': stdout.decode('latin2'),
                'stderr': stderr.decode('latin2'),
                'data': tp
            })

    # stdout, stderr, ret = execute(f"{ko_flags} {ko_cc} {' '.join(files)} -o /workdir/ubitect/all/{len_all}.ucsan")
    stdout, stderr, ret = execute(f"{ko_flags}  METADATA={os.curdir}/ko-{fn}.yaml {ko_cc} {' '.join(files)} -o {dest_dir}/{tp['original_file']}.ucsan")
    if ret != 0:
        # with ColorPrint("fail"):
        #     print(f"{path} failed at link stage")
        # print(stderr.decode('latin2'))
        return ('p3', {
            'stdout': stdout.decode('latin2'),
            'stderr': stderr.decode('latin2'),
            'data': tp
        })
    # with ColorPrint("green"):
    #     print(f"success: {path}")

def worker(args):
    pipe, tp = args
    name = f"p-{os.getpid()}"
    start_time = time.time()
    r = compile(0, tp, name)
    end_time = time.time()
    if r:
        pipe.put(r)
    else:
        pipe.put((tp['original_file'], end_time - start_time))

def reducer(pipe):
    errors = {
        "p1": [],
        "p2": [],
        "p3": []
    }
    compilation_time = []
    def _writer():
        while write_to_file:
            time.sleep(300)
            json.dump(errors, open(write_to, "w"))
            json.dump(compilation_time, open("compilation_time.json", "w"))

    threading.Thread(target=_writer, daemon=True).start()
    while True:
        item = pipe.get()
        if item == 'done':
            break
        if item[0] in errors:
            errors[item[0]].append(item[1])
        else:
            compilation_time.append(item)
        pipe.task_done()

    if write_to_file:
        json.dump(errors, open(write_to, "w"))
        json.dump(compilation_time, open("compilation_time.json", "w"))
    else:
        print(errors)

all = json.load(open("bc_list_augmented_v2.json", 'r'))

if __name__ == "__main__":
    # Example usage of the ThreadPool

    num_threads = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    work_queue = []

    for idx, tp in enumerate(all):
        if len(sys.argv) > 2:
            if tp['original_file'] != sys.argv[2]:
                continue
        work_queue.append((queue, tp))

    threading.Thread(target=reducer, args=(queue,), daemon=False).start()
    process_map(worker, work_queue, max_workers=num_threads, chunksize=1)
    queue.put('done')

# json.dump(errors, open("errors.json", "w"))

# open('tp_success.yaml', 'w').write(yaml.dump(tp_success))