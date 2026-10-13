#!/usr/bin/python3
"""Exercise an installed, isolated MyBrowser runtime against a local fixture."""
import functools
import hashlib
import http.server
import json
import os
import runpy
import subprocess
import threading
import time
from pathlib import Path
from common import HOME, REPO, desktop_env, private_json


def main():
    if any((HOME / 'profiles').iterdir()):
        raise RuntimeError('Smoke test requires an empty disposable runtime')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Handler, directory=str(REPO / 'tests'))
    fixture = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=fixture.serve_forever, daemon=True).start()
    manager = subprocess.Popen([str(HOME / 'BrowseForge'), '--base-dir', str(HOME), 'serve', '--no-open'],
                               env=desktop_env(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bridge = runpy.run_path(str(REPO / 'bin/mybrowser-mcp'), run_name='mybrowser_bridge')
    opened = []
    result = {'manager_version': '2.1.15', 'public_scan_performed': False}
    try:
        deadline = time.monotonic() + 30
        while not bridge['ready']():
            if manager.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('Smoke manager not ready')
            time.sleep(0.2)
        seeded = subprocess.run([str(REPO / 'bin/mybrowser'), 'seed-profiles'], env=os.environ,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if seeded.returncode:
            raise RuntimeError('Profile preset creation failed')
        profiles = bridge['call']('list_profiles')
        result['created_profiles'] = len(profiles)
        # Seeding is idempotent; opening profiles is a separate explicit step.
        subprocess.run([str(REPO / 'bin/mybrowser'), 'seed-profiles'], env=os.environ,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=60)
        result['seed_idempotent'] = len(bridge['call']('list_profiles')) == len(profiles)
        result['browsers'] = []
        for name in ['Firefox 1', 'Firefox 3', 'Профиль 1']:
            profile = next((p for p in profiles if p['name'] == name), None)
            if not profile:
                continue
            pid = profile['id']
            record = {'name': name, 'runtime_id': profile['runtime_id']}
            bridge['call']('open_browser', profile_id=pid)
            opened.append(pid)
            url = f'http://127.0.0.1:{fixture.server_port}/control.html'
            bridge['call']('navigate', profile_id=pid, url=url, wait_until='load')
            # Read identifiers from the committed fixture rather than a public site.
            selectors = bridge['call']('evaluate', profile_id=pid,
                                       script='() => JSON.stringify({input:"#"+document.querySelector("input").id,button:"#"+document.querySelector("button").id})')
            bridge['call']('type_text', profile_id=pid, selector=selectors['input'], text='MyBrowser smoke', clear=True)
            bridge['call']('click', profile_id=pid, selector=selectors['button'])
            state = bridge['call']('evaluate', profile_id=pid,
                                   script='() => JSON.stringify({text:document.body.textContent,ua:navigator.userAgent,platform:navigator.platform,webdriver:navigator.webdriver})')
            record['typed_and_clicked'] = 'MyBrowser smoke' in state['text']
            record['platform'] = state['platform']
            record['webdriver'] = state['webdriver']
            if not record['typed_and_clicked']:
                raise RuntimeError('MCP interaction verification failed: ' + name + ': ' + state['text'])
            if profile['runtime_id'] == 'camoufox':
                persona = HOME / 'profiles' / pid / 'browser-data/CamoufoxNative/persona.json'
                digest = hashlib.file_digest(persona.open('rb'), 'sha256').hexdigest()
                bridge['call']('close_browser', profile_id=pid)
                opened.remove(pid)
                bridge['call']('open_browser', profile_id=pid)
                opened.append(pid)
                record['persona_stable_after_restart'] = hashlib.file_digest(persona.open('rb'), 'sha256').hexdigest() == digest
                record['backend'] = json.loads((persona.parent / 'rendering.json').read_text())['backend']
                if not record['persona_stable_after_restart']:
                    raise RuntimeError('Persona changed on restart')
            bridge['call']('close_browser', profile_id=pid)
            opened.remove(pid)
            result['browsers'].append(record)
        private_json(HOME / 'smoke-result.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        for pid in opened:
            try:
                bridge['call']('close_browser', profile_id=pid)
            except Exception:
                pass
        manager.terminate()
        try:
            manager.wait(timeout=30)
        except subprocess.TimeoutExpired:
            manager.kill()
            manager.wait()
        fixture.shutdown()
        fixture.server_close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('MyBrowser smoke failed: ' + type(error).__name__)
        if isinstance(error, RuntimeError):
            print(str(error))
        raise SystemExit(1)
