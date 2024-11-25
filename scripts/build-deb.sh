#!/usr/bin/env bash
set -e

# Build the Docker image
docker build -t schulstick-builder -f docker/Dockerfile.build .

# Run the build process
docker run --rm -v "$(pwd):/build" -v "$(pwd)/dist:/dist" schulstick-builder bash -c "cd /build && dpkg-buildpackage -us -uc && mv ../schulstick* /dist" 


echo "Debian package built successfully! Check the dist/ directory."
