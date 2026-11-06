#!/usr/bin/env python3
"""Project hygiene validator.

Usage:
  python scripts/validate_project.py <project_dir> [--env-file .env] [--strict]

Checks:
  - env template present; variables tagged [required]/[optional]; optional check that a real
    env file (or the process environment) defines every [required] variable
  - .gitignore covers .env
  - likely secrets committed in source files (common key patterns)
  - tests present, CI workflow present, README present, lockfile present
  - Dockerfile: non-root USER, no ':latest' base image, no obvious secrets in ENV/ARG

Severity: ERROR fails the run; WARN fails only with --strict. Exit codes: 0 ok, 1 problems, 2 usage.
These are heuristics, not a security audit.
"""
import argparse
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build", ".mypy_cache", ".pytest_cache"}
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yml", ".yaml", ".toml", ".md", ".txt", ".env", ".cfg", ".ini", ".sh", ".tf", ".example", ""}
SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("API key (sk- style)", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
]
LOCKFILES = ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "poetry.lock", "uv.lock", "Pipfile.lock", "requirements.lock"]

findings = []


def add(level, msg):
    findings.append((level, msg))


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield os.path.join(dp, fn)


def parse_env_template(path):
    req, opt = [], []
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=", line)
        if not m:
            continue
        name = m.group(1)
        if "[required]" in line:
            req.append(name)
        elif "[optional]" in line:
            opt.append(name)
        else:
            add("WARN", f"env template: {name} is not tagged [required] or [optional]")
    return req, opt


def read_env_file(path):
    vals = {}
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*)", line)
        if m:
            vals[m.group(1)] = m.group(2).split(" #")[0].strip()
    return vals


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--env-file", help="validate this env file against the template's [required] variables")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    a = ap.parse_args()
    root = a.project_dir
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    files = list(walk(root))
    names = {os.path.relpath(f, root) for f in files}
    base = {os.path.basename(f) for f in files}

    # env template
    tmpl = next((os.path.join(root, n) for n in (".env.example", "env.example", "templates/env.example") if n in names), None)
    if not tmpl:
        add("ERROR", "no .env.example found")
    else:
        req, opt = parse_env_template(tmpl)
        if not req:
            add("WARN", "env template has no variables tagged [required]")
        if a.env_file:
            actual = read_env_file(a.env_file)
            for name in req:
                v = actual.get(name, os.environ.get(name, ""))
                if not v or v.startswith("replace"):
                    add("ERROR", f"required variable {name} is missing or still a placeholder")

    # gitignore
    gi = os.path.join(root, ".gitignore")
    if os.path.exists(gi):
        if not re.search(r"^\s*\.env\s*$|^\s*\.env\*", open(gi, encoding="utf-8", errors="ignore").read(), re.M):
            add("ERROR", ".gitignore does not ignore .env")
    else:
        add("WARN", "no .gitignore")
    if ".env" in names:
        add("WARN", ".env exists in the project directory; make sure it is not committed")

    # secret scan
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in TEXT_EXT or os.path.getsize(f) > 1_000_000 or os.path.basename(f) == "validate_project.py":
            continue
        try:
            text = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for label, pat in SECRET_PATTERNS:
            if pat.search(text):
                add("ERROR", f"possible {label} in {os.path.relpath(f, root)}")

    # tests / CI / docs / lockfile
    has_tests = any(re.search(r"(^|/)(tests?|__tests__|e2e)(/|$)", n) or re.search(r"(test_.*\.py|.*\.(test|spec)\.[jt]sx?)$", n) for n in names)
    if not has_tests:
        add("WARN", "no tests found")
    if not any(n.startswith(".github/workflows/") or n in (".gitlab-ci.yml", "Jenkinsfile") for n in names):
        add("WARN", "no CI configuration found")
    if not any(b.lower() == "readme.md" for b in base):
        add("WARN", "no README.md")
    if not any(l in base for l in LOCKFILES) and (("package.json" in base) or ("requirements.txt" in base) or ("pyproject.toml" in base)):
        add("WARN", "no dependency lockfile found (reproducible builds)")

    # Dockerfile
    for f in files:
        if os.path.basename(f) == "Dockerfile" or os.path.basename(f).startswith("Dockerfile."):
            rel = os.path.relpath(f, root)
            text = open(f, encoding="utf-8", errors="ignore").read()
            users = re.findall(r"^\s*USER\s+(\S+)", text, re.M)
            if not users or users[-1] in ("root", "0"):
                add("WARN", f"{rel}: container runs as root (add a non-root USER)")
            for img in re.findall(r"^\s*FROM\s+(\S+)", text, re.M | re.I):
                if img.lower() != "scratch" and (img.endswith(":latest") or (":" not in img and "@" not in img and img not in ("builder", "base"))):
                    add("WARN", f"{rel}: base image '{img}' is unpinned (use a version tag or digest)")
            if re.search(r"^\s*(ENV|ARG)\s+\w*(SECRET|PASSWORD|TOKEN|API_KEY)\w*\s*=\s*\S+", text, re.M | re.I):
                add("ERROR", f"{rel}: secret-looking value set in ENV/ARG")
            if not os.path.exists(os.path.join(root, ".dockerignore")):
                add("WARN", "Dockerfile present but no .dockerignore")

    errors = [m for l, m in findings if l == "ERROR"]
    warns = [m for l, m in findings if l == "WARN"]
    for l, m in findings:
        print(f"[{l}] {m}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s) across {len(files)} files scanned")
    if errors or (a.strict and warns):
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
