#!/usr/bin/env python3
build_folder = "../build"
import subprocess
import os
import sys
import glob
import argparse

import logging

# logging.basicConfig(level = logging.DEBUG ,format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')

common_env = {
    "KO_CC": "clang-12", 
    "KO_DONT_OPTIMIZE": "1",
    "KO_USE_THOROUPY": "1",
    "KO_TRACE_BB": "1",
}

ucsan_config = {
  "termination": {
    "loop": {
      "threshold": 10
    }, 
    "branch": {
      "always_true": False
    }
  }, 
  "scheduler": {
    "fifo": {
      "checksum": True
    }
  }
}

tests = []

sys.path.append('../thoroupy')

from manager import UcsanManager

for file in glob.glob("test/*.c"):
    test = [file.replace("test/","")[:-2], "", []]
    c = open(file,"r").readlines()
    for line in c:
        if line.startswith("// METADATA:"):
            test[1] = line.split(":", maxsplit=2)[1].strip()
        elif line.startswith("// ENV:"):
            test.extend(line.split(":", maxsplit=2)[1].strip().split(" "))
        elif line.startswith("// FLAG:"):
            flags = line.split(":", maxsplit=2)[1].strip().split(" ")
            for flag in flags:
                if ',' in flag:
                    f, c = flag.split(",")
                    test[2].append([int(f), int(c)])
                else:
                    test[2].append([int(flag), 0])
    tests.append(test)
    
ko_lang = f"{build_folder}/bin/ko-clang -fno-discard-value-names"

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0;0m"
colored = lambda color, text: f"{color}{text}{RESET}"

def run(cmd, cwd=build_folder, env=common_env):
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    return subprocess.run(cmd, check=True, cwd=cwd, env=env)

class Proxy():
    def __init__(self, value = ""):
        self._value = value
    def set_value(self, value):
        self._value = value
    def get(self):
        return self._value

def perform_test(stage, *args):
    stage.set_value("Start")
    env = os.environ.copy()
    env.update(common_env)

    test_name = args[0]
    metafile = args[1]
    flags = args[2]

    env['METADATA'] = "metadata/" + metafile
    for arg in args[3:]:
        env[arg] = "1"
    run(f"{ko_lang} -g -S -emit-llvm -o ll/{test_name}.ll test/{test_name}.c", cwd=".", env=env)
    run(f"{ko_lang} -g -o binary/{test_name}.ucsan test/{test_name}.c", cwd=".", env=env)
    stage.set_value('Compiled')
    if flags:
        triggered = {}
        for flag in flags:
            triggered[flag[0]] = 0
        m = UcsanManager(f'binary/{test_name}.ucsan', config=ucsan_config, terminate=False)
        m.run()
        for exit_status in m.exit_status:
            if exit_status > 255:
                exit_status = exit_status >> 8
            stage.set_value(f"Unexpected status: {exit_status}") # will be overwritten if no exception is raised
            triggered[exit_status] += 1

        message = []
        for flag in flags:
            key = flag[0]
            expected = flag[1]
            if expected == 0:
                expected = "any"
            v = triggered[flag[0]]
            message.append(f"{key}:{v}/{expected}")
        message = ",".join(message)
        stage.set_value(message)

        for flag in flags:
            if flag[1] != 0 and triggered[flag[0]] != flag[1]:
                raise Exception(f"Flag {flag[0]} triggered {triggered[flag[0]]} times, expected {flag[1]}")
            if flag[1] == 0 and triggered[flag[0]] == 0:
                raise Exception(f"Flag {flag[0]} not triggered")
        stage.set_value(f'Passed({message})')
    else:
        stage.set_value('Passed')

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
        stage = Proxy()
        if target and test[0] != target:
            continue
        if len(test[0]) > max_len:
            max_len = len(test[0]) // 16 * 16 + 16
        try:
            perform_test(stage, *test)
            tasks.append((test[0], colored(GREEN, stage.get())))
        except:
            errors += 1
            tasks.append((test[0], colored(RED, "Failed") + f"({stage.get()})"))
        
    print("\n\nTest results:")
    for task in tasks:
        print(f"{task[0]:{max_len}}: ", end="")
        print(task[1])

    if errors:
        print(f"\nOpps! Some tests failed!")
        print(f"You may use `{sys.argv[0]} test <test_name>` to run a specific test")
    sys.exit(0 if errors == 0 else 1)