git clone -n https://github.com/firesim/riscv-tools.git
cd riscv-tools
git checkout firesim
git submodule update --init

cd riscv-tests
git remote add donggyu https://github.com/donggyukim/riscv-tests.git
git fetch donggyu
git checkout large-input
git submodule update --init
cd ..

cd riscv-gnu-toolchain
git submodule init
git submodule update riscv-binutils-gdb 
git submodule update riscv-gcc
git submodule update riscv-glibc
git submodule update riscv-newlib
git submodule update riscv-dejagnu
cd ..

./build.sh
cd riscv-gnu-toolchain/build
make linux

cd ../..
