#!/bin/bash

echo stopping control
sudo kill -9 `ps aux | grep control.py | awk '{print $2}'`


echo stopping web frontend
sudo kill -9 `ps aux | grep web.py | awk '{print $2}'`

