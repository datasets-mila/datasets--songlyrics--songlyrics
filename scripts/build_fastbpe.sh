#!/bin/bash

(cd bin/fastBPE/ && \
 g++ -std=c++11 -pthread -O3 fastBPE/main.cc -IfastBPE -o fast)

(cd bin/ && ln -fs fastBPE/fast .)
