#!/usr/bin/env python3
build_folder = "../build"
import subprocess
import os
import sys
import glob
import argparse

import logging

common_env = {
    "KO_CC": "clang-12", 
    "KO_DONT_OPTIMIZE": "1",
    "KO_USE_THOROUPY": "1",
    # "KO_TRACE_BB": "1",
    # "KO_RESIGN_PTRARGS": "1",
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
  "handler": {
    "ubi_handler": {},  
    "objtrace_handler": {},
    "forward_handler": {}
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
from utils.process import populate_gdb

adapter = None

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
    options = {}
    for arg in args[3:]:
        options[arg] = "1"
    env.update(options)
    run(f"{ko_lang} -g -S -emit-llvm -o ll/{test_name}.ll test/{test_name}.c", cwd=".", env=env)
    run(f"{ko_lang} -g -o binary/{test_name}.ucsan test/{test_name}.c", cwd=".", env=env)
    stage.set_value('Compiled')
    if flags:
        triggered = {}
        for flag in flags:
            triggered[flag[0]] = 0
        m = UcsanManager(f'binary/{test_name}.ucsan', config=ucsan_config, terminate=False, env=options, adapter=adapter)
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
        stage.set_value('Passed(Compile only)')

if __name__ == "__main__":
    target = None
    args = argparse.ArgumentParser()
    args.add_argument("-p", help="The build folder", default="../build")
    args.add_argument("-v", '--verbose', help="Verbose", action="count", default=0)
    args.add_argument("-s", help="Stop immediately on error", action="store_true")
    args.add_argument("-f", "--file", help="Write log to file")
    sub_parser = args.add_subparsers(title="tools")
    parser_test = sub_parser.add_parser("test", help="Run specific tests")
    parser_test.add_argument("test_name", help="The name of the test", nargs="+")
    parser_test.add_argument("-v", '--verbose', help="Verbose", action="count", default=0)
    parser_test.add_argument("-g", '--debug', help="Debug", action="store_true", default=False)
    
    parser_clean = sub_parser.add_parser("clean", help="Clean up the test environment")
    parser_clean.set_defaults(func=lambda: run("rm -rf ll binary", cwd=".") & os._exit(0) )

    def show_test():
        print("Available tests:\n\n\t", end="")
        print("\n\t".join([test[0] for test in tests]))
        print("")
        parser_test.print_help()
        os._exit(0)
    parser_list = sub_parser.add_parser("list", help="List all tests")
    parser_list.set_defaults(func=show_test)
    
    args = args.parse_args()

    build_folder = args.p if args.p else build_folder

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(args.verbose, len(levels) - 1)]  # cap to last level index

    logging.basicConfig(level = level ,format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
    
    if args.file:
        fh = logging.FileHandler(args.file)
        fh.setLevel(level)
        logging.getLogger().addHandler(fh)
    
    if 'func' in args:
        args.func()

    if 'test_name' in args:
        target = args.test_name
    else:
        target = None
    if 'debug' in args and args.debug:
        adapter = populate_gdb

    run("make -j")
    run("make install")

    os.makedirs("ll", exist_ok=True)
    os.makedirs("binary", exist_ok=True)
    tasks = []
    max_len = 0
    errors = 0
    for test in tests:
        stage = Proxy()
        if target and test[0] not in target:
            continue
        if len(test[0]) > max_len:
            max_len = len(test[0]) // 16 * 16 + 16
        try:
            if args.verbose > 2:
                test.append("debug")
            perform_test(stage, *test)
            tasks.append((test[0], colored(GREEN, stage.get())))
        except Exception as e:
            logging.exception(e)
            errors += 1
            tasks.append((test[0], colored(RED, "Failed") + f"({stage.get()})"))
            if args.s:
                break
        
    print("\n\nTest results:")
    for task in tasks:
        print(f"{task[0]:{max_len}}: ", end="")
        print(task[1])

    if errors:
        print(f"\nOpps! Some tests failed!")
        print(f"You may use `{sys.argv[0]} test <test_name>` to run a specific test")
    sys.exit(0 if errors == 0 else 1)