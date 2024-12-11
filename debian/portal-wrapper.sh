#!/bin/bash

# Try to start the LiaScript devserver, but continue even if it fails
systemctl --user start liascript-devserver.service || true

# Launch the actual portal application
exec portal
