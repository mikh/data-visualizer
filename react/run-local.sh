#!/bin/bash

set -eo pipefail

cd react

export VITE_URL_PREFIX=http://127.0.0.1:5000
export REACT_VERSION=$(cat version)

npm run dev

echo "React runner exited."