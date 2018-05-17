#!/usr/bin/env bash

echo ""
echo "Killing all ssh tunnels!"
ps aux|grep 'ssh -N -i ./agile_data_science.pem'|grep -v grep|tr -s ' '|cut -d ' ' -f2|xargs kill
echo "All ssh tunnels killed..."
echo ""
