#!/usr/bin/env python3
"""
Sync labels from a JSON configuration file to target repositories.

This script uses the GitHub CLI (gh) to manage labels across multiple repositories
based on a JSON configuration file.
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any


def check_dependencies() -> None:
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: GitHub CLI (gh) is not installed", file=sys.stderr)
        print("Install it from: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError:
        print("Error: GitHub CLI is not authenticated", file=sys.stderr)
        print("Run: gh auth login", file=sys.stderr)
        sys.exit(1)


def load_config(config_file: Path) -> Any:
    if not config_file.exists():
        print(f"Error: Configuration file '{config_file}' does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_file) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}", file=sys.stderr)
        sys.exit(1)

    return config


def get_repo_labels(repo: str) -> Any:
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/labels", "--paginate"],
            capture_output=True,
            check=True,
            text=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def create_label(repo: str, name: str, color: str, description: str) -> bool:
    try:
        subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/{repo}/labels",
                "-f",
                f"name={name}",
                "-f",
                f"color={color}",
                "-f",
                f"description={description}",
            ],
            capture_output=True,
            check=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def update_label(repo: str, name: str, color: str, description: str) -> bool:
    encoded_name = urllib.parse.quote(name, safe="")
    try:
        subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "PATCH",
                f"repos/{repo}/labels/{encoded_name}",
                "-f",
                f"color={color}",
                "-f",
                f"description={description}",
            ],
            capture_output=True,
            check=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def sync_labels(label_config: dict[str, Any], repo_config: dict[str, Any]) -> None:
    labels = label_config["labels"]
    repo_configs = repo_config["repo_configs"]

    print(f"Found {len(labels)} labels in configuration file")

    for repo_config in repo_configs:
        repo = repo_config["repo"]
        exclude_labels = set(repo_config.get("exclude_labels", []))

        print()
        print(f"==> Syncing labels to repository: {repo}")

        existing_labels = get_repo_labels(repo)

        if not existing_labels:
            print(
                f"  Warning: Could not fetch labels from {repo} (might not exist or no permissions)"
            )

        existing_labels_dict = {label["name"]: label for label in existing_labels}

        for label in labels:
            label_name = label["name"]
            label_color = label.get("color", "ededed")
            label_description = label.get("description", "")

            if label_name in exclude_labels:
                print(f"  Skipping excluded label: {label_name}")
                continue

            existing_label = existing_labels_dict.get(label_name)

            if existing_label:
                existing_description = existing_label.get("description", "")
                existing_color = existing_label.get("color", "")

                if existing_description != label_description or existing_color != label_color:
                    print(f"  Updating label: {label_name}")
                    if not update_label(repo, label_name, label_color, label_description):
                        print(f"  Warning: Failed to update label '{label_name}'")
                else:
                    print(f"  Label unchanged: {label_name}")
            else:
                print(f"  Creating label: {label_name}")
                if not create_label(repo, label_name, label_color, label_description):
                    print(f"  Warning: Failed to create label '{label_name}'")

        print(f"  Completed syncing labels to {repo}")

    print()
    print("Label synchronization completed successfully")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync labels from a JSON configuration file to target repositories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync labels from configuration file
  %(prog)s -lc labels-config.json -rc repo-config.json

Requirements:
  - GitHub CLI (gh) must be installed and authenticated
""",
    )

    parser.add_argument(
        "-lc",
        "--label-config",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "-rc",
        "--repo-config",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to JSON configuration file",
    )

    print("Parsing arguments...")
    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Using label configuration file: {args}")
    check_dependencies()
    label_config = load_config(args.label_config)
    repo_config = load_config(args.repo_config)
    print("Starting label synchronization...")
    sync_labels(label_config, repo_config)


if __name__ == "__main__":
    main()
