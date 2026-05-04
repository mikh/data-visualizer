#!/usr/bin/env python3
"""General-purpose version bump script driven by a JSON configuration file.

Supports bumping version numbers across multiple files with dependency
cascading. Version format is <release>.<major>.<minor>.

Usage:
    version-bump.py --config <path> --bump <level>-<target>[,...] [--dry-run]

Example:
    version-bump.py --config config.json --bump minor-app,major-chart
"""

import argparse
import dataclasses
import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

import yaml

VALID_TYPES = {"version", "helm-appversion", "helm-version"}
VALID_LEVELS = {"release", "major", "minor"}


@dataclasses.dataclass
class Version:
    """Represents a three-part version number: release.major.minor."""

    release: int
    major: int
    minor: int

    _PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    @classmethod
    def parse(cls, text: str, context: str = "") -> "Version":
        """Parse an X.Y.Z version string into a Version instance."""
        text = text.strip().strip('"').strip("'")
        m = cls._PATTERN.match(text)
        if not m:
            ctx = f" (in {context})" if context else ""
            raise ValueError(f"Version '{text}'{ctx} does not match expected format X.Y.Z")
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def bump(self, level: str) -> "Version":
        """Return a new Version bumped at the given level."""
        if level == "release":
            return Version(self.release + 1, 0, 0)
        if level == "major":
            return Version(self.release, self.major + 1, 0)
        if level == "minor":
            return Version(self.release, self.major, self.minor + 1)
        raise ValueError(f"Unknown bump level: {level}")

    def as_tuple(self) -> tuple[int, int, int]:
        """Return the version as a comparable tuple."""
        return (self.release, self.major, self.minor)

    def __gt__(self, other: "Version") -> bool:
        return self.as_tuple() > other.as_tuple()

    def __str__(self) -> str:
        return f"{self.release}.{self.major}.{self.minor}"


@dataclasses.dataclass
class Target:
    """A versioned file target from the config."""

    name: str
    path: pathlib.Path
    type: str
    depends_on: list[str] = dataclasses.field(default_factory=list)


def load_config(config_path: pathlib.Path) -> dict[str, Target]:
    """Load and validate the JSON configuration file."""
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {config_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    base_dir = config_path.parent
    targets: dict[str, Target] = {}
    errors: list[str] = []

    for name, entry in raw.items():
        if "path" not in entry or "type" not in entry:
            errors.append(f"Target '{name}' missing required 'path' or 'type' field")
            continue

        resolved_path = (base_dir / entry["path"]).resolve()
        target_type = entry["type"]
        depends_on = entry.get("depends-on", [])

        if target_type not in VALID_TYPES:
            errors.append(
                f"Target '{name}' has invalid type '{target_type}'. "
                f"Valid types: {', '.join(sorted(VALID_TYPES))}"
            )

        if not resolved_path.is_file():
            errors.append(f"Target '{name}' path does not exist: {resolved_path}")

        targets[name] = Target(
            name=name, path=resolved_path, type=target_type, depends_on=depends_on
        )

    for name, target in targets.items():
        for dep in target.depends_on:
            if dep not in targets:
                errors.append(f"Target '{name}' depends on '{dep}' which is not defined in config")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    return targets


def topological_sort(targets: dict[str, Target]) -> list[str]:
    """Return target names in topological order. Detects cycles."""
    in_degree: dict[str, int] = {name: 0 for name in targets}
    children: dict[str, list[str]] = defaultdict(list)

    for name, target in targets.items():
        for parent in target.depends_on:
            children[parent].append(name)
            in_degree[name] += 1

    queue = [name for name, deg in in_degree.items() if deg == 0]
    result: list[str] = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for child in children[node]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(result) != len(targets):
        cycle_members = [name for name in targets if name not in result]
        print(
            f"ERROR: Circular dependency detected among: {', '.join(cycle_members)}",
            file=sys.stderr,
        )
        sys.exit(1)

    return result


def parse_bump_args(bump_csv: str, targets: dict[str, Target]) -> dict[str, str]:
    """Parse '--bump minor-app,major-chart' into {name: level}."""
    bumps: dict[str, str] = {}
    errors: list[str] = []

    for token in bump_csv.split(","):
        token = token.strip()
        parts = token.split("-", maxsplit=1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            errors.append(f"Invalid bump specifier '{token}'. Expected <level>-<target>")
            continue

        level, name = parts
        if level not in VALID_LEVELS:
            errors.append(
                f"Invalid bump level '{level}' in '{token}'. "
                f"Valid levels: {', '.join(sorted(VALID_LEVELS))}"
            )
            continue

        if name not in targets:
            errors.append(f"Unknown target '{name}' in '{token}'")
            continue

        if name in bumps:
            priority = {"release": 3, "major": 2, "minor": 1}
            if priority[level] > priority[bumps[name]]:
                bumps[name] = level
        else:
            bumps[name] = level

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    return bumps


def read_version(target: Target) -> Version:
    """Read the current version from a target file."""
    context = str(target.path)

    if target.type == "version":
        text = target.path.read_text(encoding="utf-8").strip()
        return Version.parse(text, context)

    data = yaml.safe_load(target.path.read_text(encoding="utf-8"))

    if target.type == "helm-appversion":
        raw = data.get("appVersion")
        if raw is None:
            print(f"ERROR: No 'appVersion' field found in {target.path}", file=sys.stderr)
            sys.exit(1)
        return Version.parse(str(raw), context)

    if target.type == "helm-version":
        raw = data.get("version")
        if raw is None:
            print(f"ERROR: No 'version' field found in {target.path}", file=sys.stderr)
            sys.exit(1)
        return Version.parse(str(raw), context)

    print(f"ERROR: Unknown target type '{target.type}'", file=sys.stderr)
    sys.exit(1)


def compute_bumps(
    targets: dict[str, Target],
    explicit_bumps: dict[str, str],
    topo_order: list[str],
) -> dict[str, tuple[Version, Version]]:
    """Compute all version changes. Returns {name: (old_version, new_version)}."""
    changes: dict[str, tuple[Version, Version]] = {}

    for name in topo_order:
        target = targets[name]
        current = read_version(target)

        if name in explicit_bumps:
            new = current.bump(explicit_bumps[name])
            changes[name] = (current, new)
        elif target.depends_on:
            bumped_parents = [changes[p][1] for p in target.depends_on if p in changes]
            if bumped_parents:
                best = max(bumped_parents, key=lambda v: (v.release, v.major))
                if (best.release, best.major) != (current.release, current.major):
                    new = Version(best.release, best.major, 1)
                else:
                    new = Version(current.release, current.major, current.minor + 1)
                changes[name] = (current, new)

    return changes


def apply_helm_regex(text: str, target_type: str, new_version: Version) -> str:
    """Apply a regex substitution to update a helm version field in-place."""
    if target_type == "helm-appversion":
        return re.sub(
            r'(appVersion:\s*")\d+\.\d+\.\d+(")',
            rf"\g<1>{new_version}\g<2>",
            text,
        )
    if target_type == "helm-version":
        return re.sub(
            r"^(version:\s*)\d+\.\d+\.\d+",
            rf"\g<1>{new_version}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    return text


def apply_all_writes(
    changes: dict[str, tuple[Version, Version]], targets: dict[str, Target]
) -> None:
    """Write all version changes to disk, batching writes per file."""
    by_file: dict[pathlib.Path, list[tuple[Target, Version]]] = defaultdict(list)

    for name, (_, new_ver) in changes.items():
        by_file[targets[name].path].append((targets[name], new_ver))

    for file_path, updates in by_file.items():
        if all(t.type == "version" for t, _ in updates):
            _, new_ver = max(updates, key=lambda x: x[1].as_tuple())
            file_path.write_text(str(new_ver) + "\n", encoding="utf-8")
        else:
            text = file_path.read_text(encoding="utf-8")
            for target, new_ver in updates:
                if target.type == "version":
                    file_path.write_text(str(new_ver) + "\n", encoding="utf-8")
                else:
                    text = apply_helm_regex(text, target.type, new_ver)
            file_path.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Bump version numbers across multiple files.")
    parser.add_argument(
        "--bump",
        default=None,
        help=(
            "Comma-separated list of <level>-<target>. "
            "Levels: release, major, minor. "
            "Example: minor-app,major-chart"
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_versions",
        help="List all targets and their current versions, then exit",
    )
    parser.add_argument(
        "--config",
        required=True,
        type=pathlib.Path,
        help="Path to the version-bump JSON config file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files",
    )
    parser.add_argument(
        "--compare-to-branch",
        action="store_true",
        dest="compare_to_branch",
        help="Compare current versions to a target branch and verify at least one was incremented",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Target branch for --compare-to-branch (default: main)",
    )
    return parser


def list_versions(targets: dict[str, Target], topo_order: list[str]) -> None:
    """Print all targets and their current versions."""
    for name in sorted(topo_order):
        target = targets[name]
        version = read_version(target)
        deps = ""
        if target.depends_on:
            deps = f"  (depends-on: {', '.join(target.depends_on)})"
        print(f"  {name}: {version}  [{target.type}]{deps}")


def _git(*cmd: str, cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result."""
    return subprocess.run(
        ["git", *cmd],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


def read_version_from_ref(target: Target, ref: str, repo_root: pathlib.Path) -> Version | None:
    """Read a target's version from a git ref.

    Returns None if the file doesn't exist on that ref.
    """
    rel_path = target.path.relative_to(repo_root)
    result = _git("show", f"{ref}:{rel_path}", cwd=repo_root)
    if result.returncode != 0:
        return None

    content = result.stdout
    context = f"{ref}:{rel_path}"

    if target.type == "version":
        return Version.parse(content.strip(), context)

    data = yaml.safe_load(content)
    helm_field = {"helm-appversion": "appVersion", "helm-version": "version"}
    field_name = helm_field.get(target.type)
    if field_name is None:
        return None
    raw = data.get(field_name)
    if raw is None:
        return None
    return Version.parse(str(raw), context)


def compare_to_branch(targets: dict[str, Target], branch: str) -> None:
    """Compare current versions to a target branch. Exit 0 if at least one incremented."""
    # Verify we're in a git repo
    result = _git("rev-parse", "--git-dir")
    if result.returncode != 0:
        print("ERROR: Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    # Verify target branch exists
    result = _git("rev-parse", "--verify", branch)
    if result.returncode != 0:
        print(f"ERROR: Branch '{branch}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Check if current HEAD is the same commit as the target branch.
    # Comparing SHAs handles detached HEAD (e.g. GitLab CI), local branches,
    # and remote refs uniformly.
    head_sha = _git("rev-parse", "HEAD").stdout.strip()
    target_sha = _git("rev-parse", branch).stdout.strip()
    if head_sha and target_sha and head_sha == target_sha:
        print(f"Current HEAD matches '{branch}', nothing to compare.")
        return

    # Get repo root for relative path computation
    result = _git("rev-parse", "--show-toplevel")
    repo_root = pathlib.Path(result.stdout.strip())

    incremented: list[str] = []
    for name in sorted(targets):
        target = targets[name]
        current = read_version(target)
        old = read_version_from_ref(target, branch, repo_root)

        if old is None:
            incremented.append(name)
            print(f"  {name}: {current} (new)")
        elif current > old:
            incremented.append(name)
            print(f"  {name}: {old} -> {current}")
        else:
            print(f"  {name}: {current} (unchanged)")

    if incremented:
        print(f"\nVersion check passed: {', '.join(incremented)} incremented.")
    else:
        print(
            f"\nERROR: No versions were incremented compared to branch '{branch}'.",
            file=sys.stderr,
        )
        sys.exit(1)


def main(args: argparse.Namespace) -> None:
    """Main entry point for the version_bump script."""

    if not args.config.is_file():
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    targets = load_config(args.config)
    topo_order = topological_sort(targets)

    if args.list_versions:
        list_versions(targets, topo_order)
        return

    if args.compare_to_branch:
        compare_to_branch(targets, args.branch)
        return

    if not args.bump:
        print("ERROR: --bump is required when not using --list", file=sys.stderr)
        sys.exit(1)

    explicit_bumps = parse_bump_args(args.bump, targets)
    changes = compute_bumps(targets, explicit_bumps, topo_order)

    if not changes:
        print("Nothing to bump.")
        return

    for name, (old, new) in changes.items():
        label = "(auto)" if name not in explicit_bumps else ""
        print(f"  {name}: {old} -> {new} {label}".rstrip())

    if args.dry_run:
        print("\nDry run — no files modified.")
    else:
        apply_all_writes(changes, targets)
        print("\nFiles updated.")


if __name__ == "__main__":
    build_args = build_parser().parse_args()
    main(build_args)
