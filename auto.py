import os
import sys
import re
import hashlib

# TAINT_OPTIONS="debug=1 output_dir=/workdir/tmp/outputs" ./a.out

class Task:
    def __init__(self, target, output_dir, debug = False):
        self.seeds = {}
        self.work_list = []
        self.session = 0
        self.target = target
        self.output_dir = output_dir
        self.debug = debug

    def putenv(self, seed):
        options = []
        if self.debug:
            options.append("debug=1")
        options.append(f"session_id={self.session}")
        options.append(f"output_dir={self.output_dir}")
        if seed:
            options.append(f"taint_file={seed}")
        os.putenv("TAINT_OPTIONS", ":".join(options))
    
    def spawn(self, seed=None):
        self.putenv(seed)
        ret = os.system(self.target)
        for seed in os.listdir(self.output_dir):
            r = re.match(f'id-\d+-{self.session}-', seed)
            if r:
                self.append_seed(os.path.join(self.output_dir, seed))
        self.session += 1
        return ret

    def append_seed(self, file):
        seed = open(file, 'rb').read()
        m = hashlib.md5()
        m.update(seed)
        h = m.hexdigest()
        if h in self.seeds:
            return
        self.seeds[h] = file
        self.work_list.append(h)
    
    def explore(self):
        while len(self.work_list) > 0:
            seed = self.seeds[self.work_list.pop()]
            ret = self.spawn(seed)
            if ret >= 0x8400: #0x8400
                print("Found bad input!")
                print(seed)
                print("ret", ret)
                break
            # print(len(self.work_list))


def main():
    if len(sys.argv) < 3:
        help()
        return
    task = Task(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 4:
        task.spawn(sys.argv.get[3])
    else:
        task.spawn()

    task.explore()

def help():
    print(f"""Usage:
python3 {sys.argv[0]} [binary] [output_dir] [iv]
""")

if __name__ == '__main__':
    main()