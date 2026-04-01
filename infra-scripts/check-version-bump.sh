#!/bin/bash

set -eo pipefail

function help {
    echo "Version Bump Check"
    echo "Verifies that at least one version number has been bumped relative to main."
    echo ""
    echo "Usage: check-version-bump.sh [options]"
    echo "Options:"
    echo "  -h | --help     : Show this help message and exit."
}

while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help | -help)
            help
            exit;;
        *)
            echo "Error: Invalid Option: $1"
            help
            exit 1;;
    esac
    shift
done

# Drone only clones the target branch; fetch main so we can compare against it
git fetch origin main:refs/remotes/origin/main 2>/dev/null || true

version_files=(
    "flask/version"
    "react/version"
    "helm-chart/data-visualizer/Chart.yaml"
)

bumped=0

for file in "${version_files[@]}"; do
    current=$(cat "$file")
    main=$(git show "origin/main:$file" 2>/dev/null) || {
        echo "  $file: new file (not on main) — counting as bumped"
        bumped=1
        continue
    }

    if [ "$current" != "$main" ]; then
        echo "  $file: changed"
        bumped=1
    else
        echo "  $file: unchanged"
    fi
done

echo ""
if [ "$bumped" -eq 1 ]; then
    echo "Version bump check passed."
else
    echo "Version bump check failed: no version files were updated relative to main."
    exit 1
fi
