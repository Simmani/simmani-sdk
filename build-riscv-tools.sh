#! /bin/bash
#
# Script to build RISC-V ISA simulator, proxy kernel, and GNU toolchain.
# Tools will be installed to $RISCV.

git clone https://github.com/ucb-bar/esp-tools.git

cd esp-tools
git submodule update --init

cd riscv-gnu-toolchain
git submodule init
git submodule update riscv-binutils-gdb
git submodule update riscv-glibc
git submodule update riscv-newlib
git submodule update riscv-dejagnu
git submodule update riscv-gcc
cd riscv-gcc
git checkout riscv-gcc-8.2.0
cd ..
cd ..

cd riscv-pk
git remote add simmani https://github.com/Simmani/riscv-pk.git
git fetch simmani
git checkout rocc
cd ..

cd riscv-tests
git remote add simmani https://github.com/Simmani/esp-tests.git
git fetch simmani
git checkout large-input
git submodule update --init
cd ..

. build.common

echo "Starting RISC-V Toolchain build process"

build_project riscv-fesvr --prefix=$RISCV
build_project riscv-isa-sim --prefix=$RISCV --with-fesvr=$RISCV
build_project riscv-gnu-toolchain --prefix=$RISCV
CC= CXX= build_project riscv-pk --prefix=$RISCV --host=riscv64-unknown-elf
build_project riscv-tests --prefix=$RISCV/riscv64-unknown-elf

$MAKE -C riscv-gnu-toolchain/build linux

echo -e "\\nRISC-V Toolchain installation completed!"
