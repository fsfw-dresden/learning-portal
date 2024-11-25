#!/bin/bash
set -e

if [ ! -d "dist" ] || [ -z "$(ls -A dist/*.deb 2>/dev/null)" ]; then
    echo "No .deb package found in dist/. Run build-deb.sh first!"
    exit 1
fi

# Build the test Docker image
docker build -t schulstick-tester -f docker/Dockerfile.test .

# Run the container with the .deb package
docker run --rm \
    -v "$(pwd)/dist:/app/dist" \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    schulstick-tester bash -c "\
        dpkg -i dist/*.deb && \
        su schulstick -c 'welcome'"

echo "Test completed!"
