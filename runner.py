import os
import sys
import re

# TAINT_OPTIONS="debug=1 output_dir=/workdir/tmp/outputs" ./a.out

def main():
    if len(sys.argv) < 3:
        help()
        return
    binary = sys.argv[1]
    od = sys.argv[2]
    if len(sys.argv) > 4:
        iv = sys.argv.get[3]
    else:
        iv = None

    _round = 0

    while True:
        out_dir = f"{od}/{_round}"
        os.system(f"rm -rf {out_dir}")
        os.system(f"mkdir -p {out_dir}")
        if iv:
            os.putenv("TAINT_OPTIONS", f"debug=1 output_dir={out_dir} taint_file={iv}")
        else:
            os.putenv("TAINT_OPTIONS", f"debug=1 output_dir={out_dir}")
        ret = os.system(binary)
        input(f"[*]ret={ret},Press enter to continue...")
        os.system(f"python3 display.py {out_dir}")
        for seed in os.listdir(out_dir):
            r = re.match('id-\d+-\d+-', seed)
            if r:
                prefix = r[0]
        while True:
            iv = os.path.join(out_dir, prefix + input("[*]Select id:"))
            print(iv)
            if not os.path.isfile(iv):
                print("Invalid file, please try again. e.g. for file id-0-0-0 the expected input is 0")
                continue
            break
        _round += 1


def help():
    print(f"""Usage:
python3 {sys.argv[0]} [binary] [output_dir] [iv]
""")

if __name__ == '__main__':
    main()