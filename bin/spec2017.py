#!/usr/bin/env python3

import os
import stat
import shutil
import argparse
from subprocess import Popen, run

SPEC_INT = [
    "00.perlbench",
    "02.gcc",
    "05.mcf",
    "20.omnetpp",
    "23.xalancbmk",
    "25.x264",
    "31.deepsjeng",
    "41.leela",
    "48.exchange2",
    "57.xz"
]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--suite", dest="suite", type=str,
                        help='suite [ intrate | intspeed ]', required=True)
    parser.add_argument("-i", "--input-type", dest="input_type", type=str,
                        help='input type [ train | test | ref ]', required=True)
    parser.add_argument("-c", "--compile", dest="compile", action='store_true',
                        help='compile binaries?', default=False)
    parser.add_argument("-r", "--run", dest="run", action='store_true',
                        help='run spike simulation?', default=False)
    parser.add_argument("--spec-dir", dest="spec_dir", help='spec directory')
    args = parser.parse_args()
    assert args.suite == 'intrate' or args.suite == 'intspeed'
    assert args.input_type == 'test' or args.input_type == 'ref' or args.input_type == 'train'

    return args

def compile_spec2017(args):
    if args.compile and args.spec_dir:
        env = os.environ.copy()
        env["SPEC_DIR"] = args.spec_dir
        run([
            "./gen_binaries.sh",
            "--compile",
            "--suite", args.suite,
            "--input", args.input_type],
        cwd="Speckle-2017", env=env, check=True)

    build_dir = os.path.join("Speckle-2017", "build", "overlay", args.suite, args.input_type)
    run_script_dir = os.path.join(
        "run-scripts", "spec2017-%s-%s" % (args.suite, args.input_type))
    if os.path.exists(run_script_dir):
        shutil.rmtree(run_script_dir)
    os.mkdir(run_script_dir)

    binaries = []
    for benchmark in SPEC_INT:
        if args.suite == 'intrate':
            name = '5' + benchmark + '_r'
        elif args.suite == 'intspeed':
            name = '6' + benchmark + '_s'

        binary = "bblvmlinux-" + name + "." + args.input_type
        binaries.append(binary)
        if args.compile:
            run_script = os.path.join(run_script_dir, name)
            with open(run_script, 'w') as _f:
                _f.write("#!bin/sh\n")
                _f.write("cd /root/%s\n" % (name))
                _f.write("./run.sh\n")
                _f.write("poweroff\n")

            os.chmod(run_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            run(["bin/generate-initramfs.sh", os.path.join(build_dir, name), run_script], check=True)
            shutil.move("bblvmlinux", binary)

    return binaries

def run_spec2017(binaries):
    ps = []
    stdouts = [open(binary + ".out", 'w') for binary in binaries]
    stderrs = [open(binary + ".err", 'w') for binary in binaries]
    for binary, stdout, stderr in zip(binaries, stdouts, stderrs):
        ps.append(Popen(["spike", "./%s" % binary],
                        stdout=stdout, stderr=stderr))

    while any(p.poll() is None for p in ps):
        pass

    assert all(p.poll() == 0 for p in ps)

if __name__ == "__main__":

    args = parse_args()
    binaries = compile_spec2017(args)
    if args.run:
        run_spec2017(binaries)
