#!/bin/bash

set -eo pipefail

cd react

export VITE_URL_PREFIX=http://127.0.0.1:5000
VITE_REACT_VERSION=$(cat version)
export VITE_REACT_VERSION
echo "$VITE_REACT_VERSION"

npm run dev

echo "React runner exited."
