#!/bin/bash

set -eo pipefail

function help {
    echo "Runs Jest tests."
    echo ""
    echo "Syntax: run-jest"
    echo "Options:"
    echo "  --log-dir               <dir>                    : Directory to write to."
}

log_dir="tmp/logs/jest"

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h)
            help
            exit 0
            ;;
        --log-dir)
            log_dir="$2"
            shift;;
        *)
            echo "Unknown argument: $1"
            help
            exit 1
            ;;
    esac
    shift
done

mkdir -p "$log_dir"
cd react

# Ensure the private @mikh registry is configured (needed in CI where .npmrc may not be present)
GITEA_INTERNAL="http://gitea-http.gitea.svc.cluster.local:3000"
npm config set @mikh:registry "$GITEA_INTERNAL/api/packages/mikh/npm/"
npm config set strict-ssl false
printf "@mikh:registry=%s/api/packages/mikh/npm/\nstrict-ssl=false\n" "$GITEA_INTERNAL" > .npmrc

# Rewrite lockfile resolved URLs to use internal gitea service (the external hostname
# git.cantrip.com is not resolvable from within Drone Docker containers)
sed -i "s|https://git.cantrip.com|$GITEA_INTERNAL|g" package-lock.json

npm install
npm test | tee "../$log_dir/jest.log"

rm -f .npmrc
