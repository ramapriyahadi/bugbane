#!/usr/bin/env python3
"""Validate bugbane skills: structure, frontmatter, version bumps, marketplace, and leak scan."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_FOLDERS = {"core", "manual", "katalon", "playwright", "appium", "ops", "meta"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://([^/\s)\"'>]+)")
IPV4_RE = re.compile(r"(?<![vV0-9.])\b(?:\d{1,3}\.){3}\d{1,3}\b(?![0-9.])")
TOKEN_RES = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]

ALLOWED_HOSTS = {
    "github.com",
    "githubusercontent.com",
    "github.io",
    "example.com",
    "example.org",
    "localhost",
    "127.0.0.1",
    "playwright.dev",
    "appium.io",
    "katalon.com",
    "figma.com",
    "atlassian.com",
    "jenkins.io",
    "cucumber.io",
    "npmjs.com",
    "skills.sh",
    "anthropic.com",
    "claude.com",
    "openai.com",
    "google.com",
    "agentskills.io",
    "semver.org",
    "keepachangelog.com",
    "conventionalcommits.org",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    """Parse minimal YAML frontmatter without external dependencies."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "frontmatter must start with '---'"

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, "frontmatter closing '---' not found"

    data: dict[str, str] = {}
    in_metadata = False
    for line in lines[1:end_idx]:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not line.startswith(" ") and not line.startswith("\t"):
            in_metadata = False
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                if key == "metadata" and not val:
                    in_metadata = True
                else:
                    data[key] = val
        elif in_metadata and ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            data[f"metadata.{key}"] = val

    return data, None


def semver_tuple(ver: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in ver.split("."))  # type: ignore[return-value]


def is_host_allowed(host: str) -> bool:
    host = host.split(":", 1)[0].lower()
    if host in ALLOWED_HOSTS:
        return True
    return any(host.endswith("." + allowed) for allowed in ALLOWED_HOSTS)


def scan_leaks(root: Path, errors: list[str]) -> None:
    targets: list[Path] = []
    for folder in ("skills", "templates", ".claude-plugin"):
        base = root / folder
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    targets.append(p)
    for name in ("README.md", "CONTRIBUTING.md"):
        p = root / name
        if p.is_file():
            targets.append(p)

    for path in targets:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # skip binary files

        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(content.splitlines(), start=1):
            for m in EMAIL_RE.finditer(line):
                email = m.group(0).lower()
                if not (
                    email.endswith("users.noreply.github.com")
                    or email.endswith("@example.com")
                    or email.endswith("@example.org")
                ):
                    errors.append(f"ERROR {rel}:{lineno}: disallowed email '{m.group(0)}'")

            for m in URL_RE.finditer(line):
                host = m.group(1)
                if not is_host_allowed(host):
                    errors.append(f"ERROR {rel}:{lineno}: non-allowlisted host '{host}'")

            for m in IPV4_RE.finditer(line):
                ip = m.group(0)
                if ip in ("127.0.0.1", "0.0.0.0"):
                    continue
                octets = [int(o) for o in ip.split(".")]
                if all(0 <= o <= 255 for o in octets):
                    errors.append(f"ERROR {rel}:{lineno}: IPv4 address '{ip}'")

            for tok_re in TOKEN_RES:
                if tok_re.search(line):
                    errors.append(f"ERROR {rel}:{lineno}: potential secret token")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate bugbane skills.")
    parser.add_argument("--base", help="Git base ref for version-bump checks.")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root path.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    skills_dir = root / "skills"

    discovered: dict[str, tuple[str, str, dict[str, str]]] = {}
    skill_files = sorted(skills_dir.rglob("SKILL.md")) if skills_dir.exists() else []

    for skill_md in skill_files:
        rel = skill_md.relative_to(root)
        parts = rel.parts
        if len(parts) != 4 or parts[0] != "skills":
            errors.append(
                f"ERROR {rel.as_posix()}: SKILL.md must be at skills/<folder>/<name>/SKILL.md"
            )
            continue

        _, folder, name, _ = parts
        if folder not in ALLOWED_FOLDERS:
            errors.append(
                f"ERROR {rel.as_posix()}: folder '{folder}' not in {sorted(ALLOWED_FOLDERS)}"
            )
            continue

        fm, parse_err = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if parse_err:
            errors.append(f"ERROR {rel.as_posix()}: {parse_err}")
            continue

        fm_name = fm.get("name", "")
        if not fm_name:
            errors.append(f"ERROR {rel.as_posix()}: missing frontmatter 'name'")
        else:
            if not NAME_RE.match(fm_name):
                errors.append(
                    f"ERROR {rel.as_posix()}: name '{fm_name}' must be lowercase kebab-case"
                )
            if len(fm_name) > 64:
                errors.append(
                    f"ERROR {rel.as_posix()}: name '{fm_name}' exceeds 64 characters"
                )
            if fm_name != name:
                errors.append(
                    f"ERROR {rel.as_posix()}: name '{fm_name}' does not match folder '{name}'"
                )

        desc = fm.get("description", "")
        if not desc:
            errors.append(f"ERROR {rel.as_posix()}: missing frontmatter 'description'")
        else:
            if len(desc) > 1024:
                errors.append(
                    f"ERROR {rel.as_posix()}: description exceeds 1024 characters ({len(desc)})"
                )
            if "<" in desc or ">" in desc:
                errors.append(
                    f"ERROR {rel.as_posix()}: description must not contain '<' or '>'"
                )

        ver = fm.get("metadata.version", "")
        if not ver or not SEMVER_RE.match(ver):
            errors.append(
                f"ERROR {rel.as_posix()}: metadata.version '{ver}' must be semver (X.Y.Z)"
            )

        skill_rel_dir = f"skills/{folder}/{name}"
        discovered[skill_rel_dir] = (folder, name, fm)

    # Version bump check
    if args.base:
        res = subprocess.run(
            ["git", "diff", "--name-only", f"{args.base}...HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            errors.append(f"ERROR git: cannot diff against {args.base}: {res.stderr.strip()}")
        else:
            changed_dirs: set[str] = set()
            for line in res.stdout.splitlines():
                p = Path(line.strip())
                if len(p.parts) >= 4 and p.parts[0] == "skills":
                    changed_dirs.add(f"skills/{p.parts[1]}/{p.parts[2]}")

            for skill_rel_dir in sorted(changed_dirs):
                if skill_rel_dir not in discovered:
                    continue
                skill_md_rel = f"{skill_rel_dir}/SKILL.md"
                show = subprocess.run(
                    ["git", "show", f"{args.base}:{skill_md_rel}"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                )
                if show.returncode != 0:
                    continue  # new skill compared to base
                old_fm, old_err = parse_frontmatter(show.stdout)
                if old_err:
                    continue
                old_ver = old_fm.get("metadata.version", "")
                new_ver = discovered[skill_rel_dir][2].get("metadata.version", "")
                if (
                    SEMVER_RE.match(old_ver)
                    and SEMVER_RE.match(new_ver)
                    and semver_tuple(new_ver) <= semver_tuple(old_ver)
                ):
                    errors.append(
                        f"ERROR {skill_md_rel}: content changed but version not bumped "
                        f"(old {old_ver}, new {new_ver})"
                    )

    # Marketplace check
    mp_path = root / ".claude-plugin" / "marketplace.json"
    if not mp_path.is_file():
        errors.append("ERROR .claude-plugin/marketplace.json: file missing")
    else:
        try:
            mp = json.loads(mp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"ERROR .claude-plugin/marketplace.json: invalid JSON: {exc}")
            mp = None

        if isinstance(mp, dict):
            plugins = mp.get("plugins", [])
            plugin_by_name = {
                p.get("name"): p for p in plugins if isinstance(p, dict) and p.get("name")
            }
            listed_paths: dict[str, list[str]] = {}
            for pname, pdata in plugin_by_name.items():
                for raw in pdata.get("skills", []):
                    norm = raw[2:] if raw.startswith("./") else raw
                    norm = norm.rstrip("/")
                    listed_paths.setdefault(norm, []).append(pname)
                    if not (root / norm / "SKILL.md").is_file():
                        errors.append(
                            f"ERROR .claude-plugin/marketplace.json: listed skill '{raw}' "
                            f"missing SKILL.md"
                        )

            for skill_rel_dir, (folder, _name, _fm) in sorted(discovered.items()):
                expected_plugin = f"bugbane-{folder}"
                if expected_plugin not in plugin_by_name:
                    errors.append(
                        f"ERROR .claude-plugin/marketplace.json: add plugin {expected_plugin}"
                    )
                    continue
                owners = listed_paths.get(skill_rel_dir, [])
                if not owners:
                    errors.append(
                        f"ERROR .claude-plugin/marketplace.json: '{skill_rel_dir}' not listed "
                        f"in {expected_plugin}"
                    )
                elif owners != [expected_plugin]:
                    errors.append(
                        f"ERROR .claude-plugin/marketplace.json: '{skill_rel_dir}' listed in "
                        f"{owners}, expected [{expected_plugin}]"
                    )

    # Leak scan
    scan_leaks(root, errors)

    for err in errors:
        print(err)
    print(f"{len(discovered)} skill(s) validated, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
