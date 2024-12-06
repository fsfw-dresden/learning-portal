#!/usr/bin/env bash

set -e

docker build  --network host -t schulstick-portal-xfce $(pwd)/dist/ || exit 1
x11docker --desktop --sudouser schulstick-portal-xfce
