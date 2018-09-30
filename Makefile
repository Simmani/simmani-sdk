all: bblvmlinux

# This setups the repository for automatic generation of ramdisk images
# by running through the manual configuration stages of linux and busybox
setup: buildroot/.config.old linux/.config.old

###############################################################################
# Get sources and configure
###############################################################################

# Busybox is a submodule. Init it before commencing
buildroot/.config: buildroot-config
	cp -f $< $@

# Configure buildroot. Hopefully this is a NOP!
buildroot/.config.old: buildroot/.config
	make -C $(@D) oldconfig

linux/.config: linux-config linux
	cp -f $< $@

# Configure linux. Hopefully this is a nop.
linux/.config.old: linux/.config
	make -C $(@D) ARCH=riscv oldconfig

###############################################################################
# Build
###############################################################################
initramfs = buildroot/output/images/rootfs.cpio
$(initramfs): buildroot/.config.old $(shell find buildroot-overlay)
	make -C buildroot -j1

busybox/busybox: busybox/.config.old profile
	@echo "Building busybox."
	time make -C $(@D) -j

linux/vmlinux: linux/.config.old $(initramfs)
	@echo "Building riscv linux."
	time make -C $(@D) -j ARCH=riscv vmlinux

bblvmlinux: linux/vmlinux
	@echo "Building an bbl instance with your payload."
	time ./build-pk.sh

clean:
	rm -rf bblvmlinux
	rm -rf riscv-pk/build
	rm -rf $(initramfs)
	rm -rf buildroot/output/target/etc/init.d/S02run

.PHONY: setup buildroot all clean
