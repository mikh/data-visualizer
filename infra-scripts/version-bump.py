#!/usr/bin/env python3
import argparse
import re
import sys


def parse_version(version_str):
    parts = version_str.strip().strip('"').split('.')
    return int(parts[0]), int(parts[1]), int(parts[2])


def format_version(release, major, minor):
    return f"{release}.{major}.{minor}"


def bump(version_tuple, bump_type):
    release, major, minor = version_tuple
    if bump_type == "major":
        return (release, major + 1, 0)
    else:
        return (release, major, minor + 1)


def read_version_file(path):
    with open(path) as f:
        return parse_version(f.read())


def write_version_file(path, version_tuple):
    with open(path, 'w') as f:
        f.write(format_version(*version_tuple) + '\n')


def read_chart(path):
    with open(path) as f:
        return f.read()


def get_chart_field(content, field):
    match = re.search(rf'^{field}:\s*"?([^"\n]+)"?', content, re.MULTILINE)
    return parse_version(match.group(1))


def set_chart_field(content, field, version_tuple):
    version_str = format_version(*version_tuple)
    if field == "appVersion":
        return re.sub(
            rf'^(appVersion:\s*)"[^"]+"',
            rf'\g<1>"{version_str}"',
            content, count=1, flags=re.MULTILINE
        )
    else:
        return re.sub(
            rf'^(version:\s*)\S+',
            rf'\g<1>{version_str}',
            content, count=1, flags=re.MULTILINE
        )


def main():
    parser = argparse.ArgumentParser(description="Bump version numbers")
    parser.add_argument("--flask-version-path", default="flask/version")
    parser.add_argument("--react-version-path", default="react/version")
    parser.add_argument("--chart-path", default="helm-chart/data-visualizer/Chart.yaml")
    parser.add_argument("--major-flask", action="store_true")
    parser.add_argument("--minor-flask", action="store_true")
    parser.add_argument("--major-react", action="store_true")
    parser.add_argument("--minor-react", action="store_true")
    parser.add_argument("--major-helm", action="store_true")
    parser.add_argument("--minor-helm", action="store_true")
    args = parser.parse_args()

    flask_bumped = False
    react_bumped = False
    any_major = False

    # Bump flask
    if args.major_flask or args.minor_flask:
        bump_type = "major" if args.major_flask else "minor"
        old = read_version_file(args.flask_version_path)
        new = bump(old, bump_type)
        write_version_file(args.flask_version_path, new)
        print(f"Flask: {format_version(*old)} -> {format_version(*new)}")
        flask_bumped = True
        if args.major_flask:
            any_major = True

    # Bump react
    if args.major_react or args.minor_react:
        bump_type = "major" if args.major_react else "minor"
        old = read_version_file(args.react_version_path)
        new = bump(old, bump_type)
        write_version_file(args.react_version_path, new)
        print(f"React: {format_version(*old)} -> {format_version(*new)}")
        react_bumped = True
        if args.major_react:
            any_major = True

    # Handle helm chart
    chart_content = read_chart(args.chart_path)
    chart_version = get_chart_field(chart_content, "version")
    app_version = get_chart_field(chart_content, "appVersion")
    app_version_modified = False
    helm_flag_passed = args.major_helm or args.minor_helm

    # Update appVersion if flask or react changed
    if flask_bumped or react_bumped:
        if any_major:
            flask_ver = read_version_file(args.flask_version_path)
            react_ver = read_version_file(args.react_version_path)
            new_major = max(flask_ver[1], react_ver[1])
            if new_major > app_version[1]:
                new_app_version = (app_version[0], new_major, 0)
            else:
                new_app_version = bump(app_version, "minor")
        else:
            new_app_version = bump(app_version, "minor")

        print(f"appVersion: {format_version(*app_version)} -> {format_version(*new_app_version)}")
        chart_content = set_chart_field(chart_content, "appVersion", new_app_version)
        app_version_modified = True

    # Update helm chart version
    if helm_flag_passed:
        bump_type = "major" if args.major_helm else "minor"
        new_chart_version = bump(chart_version, bump_type)
        print(f"Chart version: {format_version(*chart_version)} -> {format_version(*new_chart_version)}")
        chart_content = set_chart_field(chart_content, "version", new_chart_version)
    elif app_version_modified:
        new_chart_version = bump(chart_version, "minor")
        print(f"Chart version: {format_version(*chart_version)} -> {format_version(*new_chart_version)}")
        chart_content = set_chart_field(chart_content, "version", new_chart_version)

    with open(args.chart_path, 'w') as f:
        f.write(chart_content)


if __name__ == "__main__":
    main()
