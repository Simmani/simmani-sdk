## Prerequisite

* [Scons](https://scons.org): `pip install [--user] scons`

## Getting Started

* Update submodules: `git submodule update --init`
* Install RISC-V ESP Tools: `scons riscv-tools`

## Custom Benchmarks

* Add a custom benchmark to `custom/<bmark>`
* Compile its binary: `scons <bmark>`
* Build the Linux image: `scons build-<bmark>`
* Run the Linux image on Spike: `scons run-<bmark>`

## [HwachaNet](https://github.com/ucb-bar/hwacha-net)

* Three benchmarks: `squeezenet_32`, `squeezenet_encoded_32`, `squeezenet_encoded_compressed_32`
* Two versions: Scalar(`seq`), Vector(`vec`)
* Compile binaries for `pk`: `scons hwacha-net`
* Compile binaries for Linux: `scons hwacha-net-linux`
* Build Linux images: `scons build-hwacha-net`
* Run Linux images on Spike: `scons run-hwacha-net`
* Test with `pk` on Spike: `scons pk-hwacha-net`
* Clean: `scons clean-hwacha-net`

## [SPEC CPU 2017](https://www.spec.org/cpu2017/)

* Set `SPEC2017_DIR` in `config.py`
* Compile benchmark binaries: `scons spec2017{int|fp}{rate|speed}-{test|ref}`
* Build Linux images: `scons build-spec2017{int|fp}{rate|speed}-{test|ref}`
* Run Linux images on Spike: `scons run-spec2017{int|fp}{rate|speed}-{test|ref}`
* Clean: `scons -c spec2017`

## [SPEC CPU 2006](https://www.spec.org/cpu2006/)

* Set `SPEC2006_DIR` in `config.py`
* Compile benchmark binaries: `scons spec2006{int|fp}-{test|ref}`
* Build Linux images: `scons build-spec2006{int|fp}-{test|ref}`
* Run Linux images on Spike: `scons run-spec2006{int|fp}-{test|ref}`
* Clean: `scons -c spec2006`
