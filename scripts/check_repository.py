#!/usr/bin/python3
"""Reject generated/private state and accidental large artifacts before publishing."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
problems = set()
for name in filter(None, names):
    path = ROOT / name
    if not path.is_file():
        continue
    if path.stat().st_size > 10 * 1024 * 1024:
        problems.add(name + ': file exceeds 10 MiB')
    if any(part in {'browser-data', 'secrets', 'profiles', '__pycache__'} for part in path.relative_to(ROOT).parts):
        problems.add(name + ': private/generated directory')
    if path.name in {'.api-token', 'profile.json', 'TestProxy', 'Test Proxy'}:
        problems.add(name + ': private state')
    if path.suffix in {'.png', '.jpg', '.webp'}:
        continue
    text = path.read_text(errors='replace')
    if str(Path.home()) + '/' in text:
        problems.add(name + ': machine-specific home path')
    if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text):
        problems.add(name + ': private key')
    if re.search(r'gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}|sk-proj-[A-Za-z0-9_-]{30,}', text):
        problems.add(name + ': credential pattern')
if problems:
    print('\n'.join(sorted(problems)))
    raise SystemExit(1)
print('Repository check passed: no private runtime state, known token patterns, or large binaries')
