#!/bin/bash

echo `env`
echo alias chromium=\"chromium --no-sandbox --disable-gpu http://namenode:9870 http://historyserver:8188 \" > ~/.bashrc

sleep infinity
