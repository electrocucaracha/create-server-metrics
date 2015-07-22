#!/bin/bash

export PATH=/usr/local/graphviz/bin:$PATH

dot -Tsvg $1.dot -o $1.svg
