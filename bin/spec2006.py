#!/usr/bin/env python

import os
import stat
import shutil
import argparse
from subprocess import check_call

SPEC_INT = [
    "400.perlbench",
    "401.bzip2",
    "403.gcc",
    "429.mcf",
    "445.gobmk",
    "456.hmmer",
    "458.sjeng",
    "462.libquantum",
    "464.h264ref",
    "471.omnetpp",
    "473.astar",
    "483.xalancbmk"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-type", dest="input_type", type=str,
                        help='input type (test of ref)', default="test", required=False)
    args = parser.parse_args()

    assert args.input_type == 'test' or args.input_type == 'ref'

    run_script_dir = os.path.join("run-scripts", "spec2006-" + args.input_type)
    if os.path.exists(run_script_dir):
        shutil.rmtree(run_script_dir)
    os.mkdir(run_script_dir)

    out_dir = os.path.join("Speckle-2006", "riscv-spec-%s" % (args.input_type))
    for benchmark in SPEC_INT:
        binary = benchmark.split(".")[1]
        if benchmark == "483.xalancbmk":
            binary = "Xalan"
        command_file = os.path.join(
            out_dir, "commands", ".".join([benchmark, args.input_type, "cmd"]))

        with open(command_file, 'r') as _f:
            lines = _f.readlines()

        lines = [line.strip() for line in lines]

        run_script = os.path.join(run_script_dir, benchmark)
        with open(run_script, 'w') as _f:
            _f.write("#!bin/sh\n")
            _f.write("cd /root/%s\n" % (benchmark))
            for line in lines:
                _f.write("./%s %s\n" % (binary, line))
            _f.write("poweroff\n")

        os.chmod(run_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                 stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        check_call(["bin/generate-initramfs.sh", os.path.join(out_dir, benchmark), run_script])

        shutil.move("bblvmlinux", "bblvmlinux-" + benchmark + "." + args.input_type)

if __name__ == '__main__':
    main()
