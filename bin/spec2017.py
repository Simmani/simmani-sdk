#!/usr/bin/env python

import os
import stat
import shutil
import argparse
from subprocess import check_call

spec_int = [
  "00.perlbench",
  "03.gcc",
  "05.mcf",
  "20.omnetpp",
  "23.xalancbmk",
  "25.x264"
  "31.deepsjeng",
  "41.leela",
  "48.exchange2",
  "57.xz"
]

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--suite", dest="suite", type=str,
                    help='suite [ intrate | intspeed ]', required=True)
parser.add_argument("-i", "--input-type", dest="input_type", type=str,
                    help='input type [ train | test | ref ]', required=True)
args = parser.parse_args()

assert args.suite == 'intrate' or args.suite == 'intspeed'
assert args.input_type == 'test' or args.input_type == 'ref' or args.input_type == 'train'

build_dir = os.path.join("Speckle-2017", "build", "overlay", args.suite, args.input_type)
run_script_dir = os.path.join(
  "run-scripts", "spec2017-%s-%s" % (args.suite, args.input_type))
if os.path.exists(run_script_dir):
  shutil.rmtree(run_script_dir)
os.mkdir(run_script_dir)

for p in spec_int:
  if args.suite == 'intrate':
    name = '5' + p + '_r'
  elif args.suite == 'intspeed':
    name = '6' + p + '_s'

  run_script = os.path.join(run_script_dir, name)
  with open(run_script, 'w') as f:
    f.write("#!bin/sh\n")
    f.write("cd /root/%s\n" % (name))
    f.write("./run.sh\n")
    f.write("poweroff\n")

  os.chmod(run_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

  check_call(["bin/generate-initramfs.sh", os.path.join(build_dir, name), run_script])

  shutil.move("bblvmlinux", "bblvmlinux-" + name + "." + args.input_type)
