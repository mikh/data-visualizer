[group("run")]
run-local:
    ./infra-scripts/run-all.sh

[group("run")]
run-test-mode:
    ./infra-scripts/run-all.sh --test

[group("test")]
pytests:
    ./infra-scripts/run-pytests.sh

[group("test")]
jest:
    cd react && npm test

[group("test")]
cypress:
    ./infra-scripts/run-cypress.sh

[group("test")]
test-all: pytests jest cypress

[group("build")]
build-image:
    ./infra-scripts/build-image.sh --push --git-tag --latest --image-path harbor.cantrip.com/webapps/data-visualizer/flask

[group("helm")]
helm-install:
    helm install data-visualizer helm-chart/data-visualizer -n data-visualizer -f helm-chart/data-visualizer/secret-values.yaml

[group("helm")]
helm-upgrade:
    helm upgrade data-visualizer helm-chart/data-visualizer -n data-visualizer -f helm-chart/data-visualizer/secret-values.yaml

[group("version")]
version-list:
    uv run python infra-scripts/version_bump.py \
        --config infra-scripts/version-config.json \
        --list

[group("version")]
version-bump flags:
    uv run python infra-scripts/version_bump.py \
        --config infra-scripts/version-config.json \
        --bump "{{flags}}"
