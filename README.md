# Data Visualizer

Full-stack web app for uploading, organizing, and visualizing CSV/JSON data files. See `CLAUDE.md` for architecture and directory layout.

## Local development

```bash
./infra-scripts/run-all.sh
```

## Linting and formatting

CI runs four parallel lint jobs (Python, Bash, React, Helm) on every build and fails on errors. Run the same checks locally before pushing via `pre-commit` (recommended) or by invoking each tool directly.

### Tool summary

| Language | Lint       | Format             |
| -------- | ---------- | ------------------ |
| Python   | ruff       | ruff format        |
| Bash     | shellcheck | shfmt              |
| React    | eslint     | prettier           |
| Helm     | helm lint  | (n/a)              |

Python (`ruff`, `pre-commit`) and React (`prettier`) tools are installed via `flask/requirements.txt` and `react/package.json`. The tools below are external binaries and must be installed on your system.

### Installing external tools

**shellcheck** (bash linter)

```bash
# Debian/Ubuntu
sudo apt-get install shellcheck

# macOS
brew install shellcheck
```

**shfmt** (bash formatter)

```bash
# Debian/Ubuntu — download the latest binary
curl -sSfL -o /tmp/shfmt https://github.com/mvdan/sh/releases/download/v3.8.0/shfmt_v3.8.0_linux_amd64
sudo install -m 755 /tmp/shfmt /usr/local/bin/shfmt

# macOS
brew install shfmt
```

**helm** (helm chart linter)

```bash
# Debian/Ubuntu
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update && sudo apt-get install helm

# macOS
brew install helm
```

### Setting up pre-commit

Install Python deps and enable the hook:

```bash
pip install -r flask/requirements.txt
pre-commit install
```

After that, `git commit` will run formatters and linters against staged files. To run all hooks against the whole repo:

```bash
pre-commit run --all-files
```

### Running linters directly

```bash
# Python
ruff check flask infra-scripts
ruff format flask infra-scripts

# Bash
shellcheck infra-scripts/*.sh flask/*.sh react/*.sh
shfmt -w -i 2 -ci infra-scripts/*.sh flask/*.sh react/*.sh

# React
cd react && npm run lint
cd react && npm run format

# Helm
helm lint helm-chart/data-visualizer
```
