"""Paths and private file handling shared by MyBrowser entry points."""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get('MYBROWSER_HOME', Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'mybrowser')).expanduser().resolve()


def private_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix(path.suffix + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    temporary.chmod(0o600)
    temporary.replace(path)


def desktop_env():
    runtime = Path(f'/run/user/{os.getuid()}')
    env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime),
               DBUS_SESSION_BUS_ADDRESS=f'unix:path={runtime}/bus')
    env.setdefault('DISPLAY', ':0')
    authorities = list(runtime.glob('.mutter-Xwaylandauth.*'))
    if authorities:
        env['XAUTHORITY'] = str(max(authorities, key=lambda p: p.stat().st_mtime))
    return env


def load_proxy(source=None):
    """Read one HTTP proxy locally; parsing errors never contain its values."""
    from urllib.parse import urlsplit, unquote
    source = Path(source) if source else HOME / 'secrets/http-proxy.txt'
    try:
        lines = [s.strip() for s in source.read_text().splitlines() if s.strip()]
        if len(lines) != 1:
            raise ValueError()
        value = lines[0]
        if '://' in value:
            scheme, value = value.split('://', 1)
            if scheme.lower() != 'http':
                raise ValueError()
        if '@' in value:
            parsed = urlsplit('http://' + value)
            host, port = parsed.hostname, parsed.port
            username, password = unquote(parsed.username or ''), unquote(parsed.password or '')
        elif value.startswith('['):
            host, rest = value[1:].split(']:', 1)
            port, username, password = rest.split(':', 2)
            port = int(port)
        else:
            host, port, username, password = value.split(':', 3)
            port = int(port)
        if not host or not 0 < port < 65536 or not username or not password:
            raise ValueError()
        if any(c in host + username + password for c in '\r\n\x00'):
            raise ValueError()
        return dict(type='http', host=host, port=port, username=username, password=password)
    except (OSError, ValueError, TypeError):
        raise ValueError('Invalid or unreadable HTTP proxy file') from None
