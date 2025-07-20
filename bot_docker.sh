#!/bin/bash

DEBUG=${1}

docker run -it --rm -v /home/sandbox/SALbot/:/app bot:latest $DEBUG