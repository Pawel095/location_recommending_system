#!/bin/bash

echo `env`
echo alias chromium=\"chromium --no-sandbox --disable-gpu http://namenode:9870 http://historyserver:8188 \" >> ~/.bashrc
echo source \"$HOME/.sdkman/bin/sdkman-init.sh\" >> ~/.bashrc

sleep infinity
