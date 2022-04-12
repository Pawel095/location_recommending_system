#!/bin/bash

echo `env`
echo alias chrome=\"chromium --no-sandbox --disable-gpu http://namenode:9870 http://historyserver:8188\" > ~/.bashrc

sleep infinity
