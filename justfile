run-local:
    ./infra-scripts/run-all.sh

run-test-mode:
    ./infra-scripts/run-all.sh --test

pytests:
    ./infra-scripts/run-pytests.sh

build-flask-image:
    ./infra-scripts/build-flask-image.sh --push --git-tag --latest --image-path harbor.cantrip.com/webapps/data-visualizer/flask

build-react-image:
    ./infra-scripts/build-react-image.sh --push --git-tag --latest --image-path harbor.cantrip.com/webapps/data-visualizer/react

helm-install:
    helm install data-visualizer helm-chart/data-visualizer -n data-visualizer -f helm-chart/data-visualizer/secret-values.yaml

helm-upgrade:
    helm upgrade data-visualizer helm-chart/data-visualizer -n data-visualizer -f helm-chart/data-visualizer/secret-values.yaml
