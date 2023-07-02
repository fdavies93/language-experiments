#!/bin/bash
llc -filetype=obj math.ll -o math.o
clang math.o -no-pie -o math
./math || echo $?