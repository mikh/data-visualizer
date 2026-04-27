#!/bin/bash

set -exo pipefail

function help {
  echo "Build the combined Flask+React image"
  echo "Usage: build-image.sh [options]"
  echo "Options:"
  echo "  -h | --help | -help    : Show this help message and exit."
  echo "  --push                 : Push the image to the registry."
  echo "  --image-path           : Path to the image file."
  echo "  --git-tag              : Push via git branch tag."
  echo "  --latest               : Push as latest image."
  echo "  --tag                  : Custom tag for the image."
}

push=false
image_path=""
use_git_tag=false
latest=false
tag=""

while [ $# -gt 0 ]; do
  case "$1" in
    -h | --help | -help)
      help
      exit
      ;;
    --push)
      push=true
      ;;
    --image-path)
      image_path="$2"
      shift
      ;;
    --git-tag)
      use_git_tag=true
      ;;
    --latest)
      latest=true
      ;;
    --tag)
      tag="$2"
      shift
      ;;
    *)
      echo "Error: Invalid Option: $1"
      help
      exit 1
      ;;
  esac
  shift
done

git_tag=""
latest_tag=""
version=$(grep '^appVersion:' helm-chart/data-visualizer/Chart.yaml | sed 's/appVersion: *"\(.*\)"/\1/')
react_version=$(cat react/version)

if [ "$push" = true ]; then
  if [ "$use_git_tag" = true ]; then
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    current_branch=$(echo "$current_branch" | tr '/' '-')
    git_tag="${current_branch}-${version}"
  fi

  if [ "$latest" = true ]; then
    latest_tag="${version}"
  fi

  if [ -z "$image_path" ]; then
    echo "Error: Image path is required"
    help
    exit 1
  fi

  if [ -z "$git_tag" ] && [ -z "$latest_tag" ] && [ -z "$tag" ]; then
    echo "Error: No tag specified"
    help
    exit 1
  fi
fi

tag_flags=()

if [ -n "$git_tag" ]; then
  tag_flags+=(--tag "${image_path}:$git_tag")
fi

if [ -n "$latest_tag" ]; then
  tag_flags+=(--tag "${image_path}:$latest_tag")
fi

if [ -n "$tag" ]; then
  tag_flags+=(--tag "${image_path}:$tag")
fi

docker build \
  --network=host \
  --build-arg REACT_VERSION="${react_version}" \
  --build-arg NPM_REGISTRY="${NPM_REGISTRY:-https://git.cantrip.com/api/packages/mikh/npm/}" \
  "${tag_flags[@]}" \
  .

if [ "$push" = true ]; then
  if [ -n "$git_tag" ]; then
    docker push "${image_path}:$git_tag"
  fi
  if [ -n "$latest_tag" ]; then
    docker push "${image_path}:$latest_tag"
  fi
  if [ -n "$tag" ]; then
    docker push "${image_path}:$tag"
  fi
fi
