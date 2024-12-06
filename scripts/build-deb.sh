#!/usr/bin/env bash
set -e

# Create dist directory if it doesn't exist
mkdir -p dist
# Build the Docker image
docker build -t schulstick-builder -f docker/Dockerfile.build .

# Run the build process
docker run --rm --network host -v "$(pwd):/build" schulstick-builder bash -c "\
    dpkg-buildpackage -us -uc && \
    find .. -name '*.deb' -exec dpkg -c {} \; && \
    cp ../*.deb dist/"

echo "Build complete. Check ./dist for the debian package."

