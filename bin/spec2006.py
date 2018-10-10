#!/usr/bin/env python

import os
import stat
import shutil
import argparse
from subprocess import check_call

spec_int = [
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

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", dest="dir", type=str,
                    help='Speckle output directory', required=True)
parser.add_argument("-i", "--input-type", dest="input_type", type=str,
                    help='input type (test of ref)', default="test", required=False)
args = parser.parse_args()

assert args.input_type == 'test' or args.input_type == 'ref'

run_script_dir = os.path.join("run-scripts", "spec2006-" + args.input_type)
if os.path.exists(run_script_dir):
  shutil.rmtree(run_script_dir)
os.mkdir(run_script_dir)

for p in spec_int:
  binary = p.split(".")[1]
  if p == "483.xalancbmk":
    binary = "Xalan"
  command_file = os.path.join(
    args.dir, "commands", ".".join([p, args.input_type, "cmd"]))

  with open(command_file, 'r') as f:
    lines = f.readlines()

  lines = [line.strip() for line in lines]

  run_script = os.path.join(run_script_dir, p)
  with open(run_script, 'w') as f:
    f.write("#!bin/sh\n")
    f.write("cd /root/%s\n" % (p))
    for line in lines:
      f.write("./%s %s\n" % (binary, line))
    f.write("poweroff\n")

  os.chmod(run_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

  check_call(["bin/generate-initramfs.sh", os.path.join(args.dir, p), run_script])

  shutil.move("bblvmlinux", "bblvmlinux-" + p + "." + args.input_type)
