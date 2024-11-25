#!/bin/bash
set -e

# Build the Docker image
docker build -t schulstick-builder -f docker/Dockerfile.build .

# Run the build process
docker run --rm -v "$(pwd):/build" schulstick-builder bash -c "cd /build && dpkg-buildpackage -us -uc"

# Move the .deb file to a dist directory
mkdir -p dist
mv ../*.deb dist/

echo "Debian package built successfully! Check the dist/ directory."
