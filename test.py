#!/usr/bin/env python3
build_folder = "../build"
import subprocess
import os
import sys

common_env = {
    "KO_CC": "clang-12", 
    "KO_DONT_OPTIMIZE": "1",
    "KO_USE_THOROUPY": "1",
    "KO_TRACE_BB": "1",
}
tests = [
    # [test_name, metadata_file, ...additional env vars...]
    ['global', 'note.yaml', 'KO_WRAP_INDIRECT_CALL'],
    ['linklist', 'note.yaml'],
    ['external', 'note.yaml'],
    ['array', 'note.yaml'],
    ['malloc', 'note.yaml'],
    ['struct', 'struct.yaml'],
    ['backlog', 'backlog.yaml'],
    ['indirect', 'note.yaml', 'KO_WRAP_INDIRECT_CALL'],
    ['pseudo_pointer', 'note.yaml'],
    ['container_of', 'note.yaml'],
    ['loop', 'note.yaml'],
    ['asm', 'note.yaml'],
    ['ubi', 'note.yaml', "KO_CHECKER_UBI"],
]

ko_lang = f"{build_folder}/bin/ko-clang -fno-discard-value-names"

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0;0m"
colored = lambda color, text: f"{color}{text}{RESET}"

def run(cmd, cwd=build_folder, env=common_env):
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    return subprocess.run(cmd, check=True, cwd=cwd, env=env)

def perform_test(*args):
    env = os.environ.copy()
    env.update(common_env)

    test_name = args[0]
    metafile = args[1]

    env['METADATA'] = "metadata/" + metafile
    for arg in args[2:]:
        env[arg] = "1"
    run(f"{ko_lang} -g -S -emit-llvm -o ll/{test_name}.ll test/{test_name}.c", cwd=".", env=env)
    run(f"{ko_lang} -g -o binary/{test_name}.ucsan test/{test_name}.c", cwd=".", env=env)

if __name__ == "__main__":
    target = None
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            target = sys.argv[2]
        elif sys.argv[1] == 'clean':
            run("rm -rf ll binary", cwd=".")
            sys.exit(0)
        else:
            build_folder = sys.argv[1]

    run("make -j")
    run("make install")

    os.makedirs("ll", exist_ok=True)
    os.makedirs("binary", exist_ok=True)
    tasks = []
    max_len = 0
    errors = 0
    for test in tests:
        if target and test[0] != target:
            continue
        if len(test[0]) > max_len:
            max_len = len(test[0]) // 16 * 16 + 16
        try:
            perform_test(*test)
            tasks.append((test[0], colored(GREEN, 'Passed')))
        except subprocess.CalledProcessError as e:
            errors += 1
            tasks.append((test[0], colored(RED, 'Failed')))
        
    print("\n\nTest results:")
    for task in tasks:
        print(f"{task[0]:{max_len}}: ", end="")
        print(task[1])

    if errors:
        print(f"\nOpps! Some tests failed!")
        print(f"You may use `{sys.argv[0]} test <test_name>` to run a specific test")