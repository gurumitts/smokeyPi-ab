#!/bin/bash

echo starting control with target temp: $1
nohup python control.py $1 >control.log 2>&1 &

echo starting web frontend
nohup python web.py >web.log 2>&1 &
