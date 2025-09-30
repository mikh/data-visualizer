#!/bin/bash

set -eo pipefail

cd react

export VITE_URL_PREFIX=http://127.0.0.1:5000

npm run dev

echo "React runner exited."