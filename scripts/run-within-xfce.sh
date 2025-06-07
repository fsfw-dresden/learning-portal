#!/usr/bin/env bash

set -e

docker build  --network host -t learning-portal-portal-xfce $(pwd)/dist/ || exit 1
x11docker --desktop --sudouser learning-portal-portal-xfce
