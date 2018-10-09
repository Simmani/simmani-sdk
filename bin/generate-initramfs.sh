#!/usr/bin/env bash

APP=$(realpath $1)
SCRIPT=$(realpath $2)
ROOT=buildroot-overlay/root

rm -rf buildroot/output/target/root
rm -rf $ROOT
mkdir $ROOT

cp -r $APP $ROOT/
cp $SCRIPT buildroot-overlay/etc/init.d/rcS

make
