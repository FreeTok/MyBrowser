#!/usr/bin/python3
"""Build pinned manager, install browser engines and isolated user services."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from common import HOME, REPO, desktop_env, private_json


def systemd_quote(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'


def download_camoufox():
    pin = json.loads((REPO / 'config/versions.json').read_text())['camoufox']
    with tempfile.TemporaryDirectory(prefix='mybrowser-download-') as temporary:
        archive = Path(temporary) / 'camoufox.zip'
        print('Downloading pinned Camoufox', flush=True)
        with urllib.request.urlopen(pin['url'], timeout=60) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
        with archive.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != pin['sha256'] or archive.stat().st_size != pin['size']:
            raise RuntimeError('Camoufox archive checksum mismatch')
        destination = HOME / 'browsers/camoufox-current'
        destination.mkdir(mode=0o700, parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as entries:
            for entry in entries.infolist():
                target = (destination / entry.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise RuntimeError('Unsafe archive member')
                entries.extract(entry, destination)
                mode = (entry.external_attr >> 16) & 0o777
                if mode:
                    target.chmod(mode)


def write_services():
    directory = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'systemd/user'
    directory.mkdir(parents=True, exist_ok=True)
    env = desktop_env()
    service = '\n'.join([
        '[Unit]', 'Description=MyBrowser local profile manager',
        'Wants=mybrowser-proxy-direct.service', 'After=mybrowser-proxy-direct.service', '',
        '[Service]', 'Type=simple', 'WorkingDirectory=' + systemd_quote(HOME),
        'ExecStart=' + systemd_quote(HOME / 'BrowseForge') + ' --base-dir ' + systemd_quote(HOME) + ' serve --host 127.0.0.1 --no-open',
        *['Environment=' + systemd_quote(key + '=' + env[key]) for key in ['DISPLAY', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS'] if key in env],
        'UMask=0077', 'Restart=on-failure', 'RestartSec=3', 'TimeoutStopSec=25',
        'StandardOutput=null', 'StandardError=null', '',
    ])
    relay = '\n'.join([
        '[Unit]', 'Description=MyBrowser proxy bridge on physical interface', 'PartOf=mybrowser.service',
        'ConditionPathExists=' + systemd_quote(HOME / 'secrets/http-proxy.txt'), '', '[Service]',
        'Type=simple', 'ExecStart=' + systemd_quote(REPO / 'bin/mybrowser-proxy-direct'),
        'Environment=' + systemd_quote('MYBROWSER_HOME=' + str(HOME)),
        'UMask=0077', 'Restart=on-failure', 'RestartSec=2',
        'StandardOutput=null', 'StandardError=null', '',
    ])
    (directory / 'mybrowser.service').write_text(service)
    (directory / 'mybrowser-proxy-direct.service').write_text(relay)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], env=env, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--go', default=os.environ.get('MYBROWSER_GO', 'go'))
    parser.add_argument('--reuse-browsers', type=Path, help='Existing browsers directory; copy only engines')
    parser.add_argument('--skip-services', action='store_true')
    parser.add_argument('--port', type=int, default=19290)
    parser.add_argument('--relay-port', type=int, default=19299)
    args = parser.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        parser.error('Current pinned setup supports Linux x86_64')
    if not 0 < args.port < 65536 or not 0 < args.relay_port < 65536 or args.port == args.relay_port:
        parser.error('Choose two distinct valid ports')
    HOME.mkdir(mode=0o700, parents=True, exist_ok=True)
    HOME.chmod(0o700)
    for name in ['profiles', 'data', 'logs', 'browsers', 'secrets']:
        (HOME / name).mkdir(mode=0o700, exist_ok=True)
    print('Building BrowseForge 2.1.15 with SOCKS5 IPv6 fix', flush=True)
    subprocess.run([args.go, 'build', '-trimpath', '-ldflags=-s -w -X main.Version=2.1.15',
                    '-o', str(HOME / 'BrowseForge'), './cmd/server'], cwd=REPO / 'vendor/BrowseForge', check=True)
    if args.reuse_browsers:
        for name in ['camoufox-current', 'browseforge-chromium']:
            source = args.reuse_browsers.resolve() / name
            target = HOME / 'browsers' / name
            if source.is_dir() and not target.exists():
                subprocess.run(['cp', '-a', '--reflink=auto', str(source), str(target)], check=True)
    if not (HOME / 'browsers/camoufox-current/camoufox-bin').exists():
        download_camoufox()
    chromium = (HOME / 'browsers/browseforge-chromium/chrome').exists()
    config = {
        'host': '127.0.0.1', 'port': str(args.port), 'profiles_dir': 'profiles', 'data_dir': 'data',
        'log_file': 'logs/server.log', 'fingerprint_dir': 'data', 'default_runtime_id': 'camoufox',
        'humanize': {'enabled': False},
        'runtimes': {
            'camoufox': {'enabled': True, 'binary_path': str(REPO / 'bin/mybrowser-camoufox-launch'),
                        'skip_auto_update': True, 'family': 'firefox', 'display_name': 'MyBrowser Firefox'},
            'browseforge-chromium': {'enabled': chromium, 'binary_path': str(REPO / 'bin/mybrowser-chromium-launch'),
                                   'skip_auto_update': True, 'family': 'chromium', 'display_name': 'MyBrowser Chromium',
                                   'settings': {'target_platform_policy': 'strict', 'fingerprint_platform': 'linux'}},
            'cloakbrowser': {'enabled': False},
        },
    }
    if not (HOME / 'config.json').exists():
        private_json(HOME / 'config.json', config)
    if not (HOME / 'relay-config.json').exists():
        private_json(HOME / 'relay-config.json', {'port': args.relay_port})
    subprocess.run([str(HOME / 'BrowseForge'), '--base-dir', str(HOME), 'playwright', 'install-driver'], check=True)
    if not args.skip_services:
        write_services()
    print('Installed MyBrowser. Existing profiles/config were preserved.', flush=True)


if __name__ == '__main__':
    main()
