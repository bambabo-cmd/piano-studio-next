#!/usr/bin/env python3
"""Build a separate deployable app from the pinned, unchanged v1 checkout.

Python 3.10+, standard library only. Does not modify the upstream checkout.
GitHub Actions retrieves the upstream checkout; no network access in this builder.
"""
from __future__ import annotations
import argparse
import importlib.util
from html.parser import HTMLParser
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_typing_spec = importlib.util.spec_from_file_location('next_typed_note_patch', ROOT/'tools'/'typed_note_patch.py')
TYPING = importlib.util.module_from_spec(_typing_spec)
_typing_spec.loader.exec_module(TYPING)
CONFIG = json.loads((ROOT / 'upstream.json').read_text(encoding='utf-8'))
VERSION = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
HEAD_A = '<!-- PIANO_STUDIO_NEXT_HEAD_START -->\n'
HEAD_B = '<!-- PIANO_STUDIO_NEXT_HEAD_END -->\n'
BODY_A = '<!-- PIANO_STUDIO_NEXT_BODY_START -->\n'
BODY_B = '<!-- PIANO_STUDIO_NEXT_BODY_END -->\n'
REQUIRED_IDS = ('mpOpen', 'mpStart', 'mpClose', 'metroPanel', 'recBtn', 'playBtn',
                'shOpen', 'tracks', 'roll', 'exMidi', 'exJson', 'imJson', 'newTrackBtn', 'typeBtn')

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run_git(source: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()

def validate_checkout(source: Path) -> str:
    commit = run_git(source, 'rev-parse', 'HEAD')
    if commit != CONFIG['commit']:
        raise ValueError(f'Wrong original commit: {commit}; expected {CONFIG["commit"]}')
    subprocess.run(['git', '-C', str(source), 'diff', '--quiet', 'HEAD', '--',
                    *CONFIG['runtime_files']], check=True)
    tracked = set(run_git(source, 'ls-tree', '-r', '--name-only', 'HEAD').splitlines())
    if tracked != set(CONFIG['runtime_files']):
        raise ValueError('The pinned repository file inventory differs from the reviewed inventory.')
    return commit

def closing_offset(text, tag):
    # Ignore </body> or </head> inside original print/export JavaScript strings.
    offsets=[0]
    for match in re.finditer('\n',text): offsets.append(match.end())
    class Parser(HTMLParser):
        def __init__(self): super().__init__(convert_charrefs=False); self.matches=[]
        def handle_endtag(self,name):
            if name==tag:
                line,col=self.getpos();self.matches.append(offsets[line-1]+col)
    parser=Parser();parser.feed(text)
    if len(parser.matches)!=1: raise ValueError(f'Expected one actual </{tag}>; got {len(parser.matches)}')
    return parser.matches[0]

def patch_html(raw: bytes) -> tuple[bytes, dict]:
    text = raw.decode('utf-8')
    original = text
    if HEAD_A in text or BODY_A in text:
        raise ValueError('Already patched input; use the unchanged v1 checkout.')
    for ident in REQUIRED_IDS:
        if not re.search(r'\bid\s*=\s*[\'"]' + re.escape(ident) + r'[\'"]', text):
            raise ValueError(f'Original app control missing: {ident}')
    if 'function mpWire(' not in text:
        raise ValueError('Expected original metronome wiring is absent.')
    text, changes = TYPING.apply(text)
    def replace(old: str, new: str, minimum: int = 1, exact: int | None = None) -> None:
        nonlocal text
        count = text.count(old)
        if count < minimum or (exact is not None and count != exact):
            raise ValueError(f'Unexpected source anchor count {count}: {old[:70]!r}')
        if new in text:
            raise ValueError('Replacement already exists; refusing an ambiguous inverse patch.')
        text = text.replace(old, new)
        changes.append({'old': old, 'new': new, 'count': count})
    replace('<title>우리집 연주실</title>', '<title>우리집 연주실 2 · Piano Studio Next</title>', exact=1)
    replace('<h1>우리집 연주실</h1>', '<h1>우리집 연주실 2</h1>', exact=1)
    replace('name="apple-mobile-web-app-title" content="우리집 연주실"',
            'name="apple-mobile-web-app-title" content="우리집 연주실 2"', exact=1)
    replace("indexedDB.open('home-piano-studio',1)",
            "indexedDB.open('piano-studio-next-v2',1)", exact=1)
    # Original localStorage keys include both fixed strings and 'hps-'+cls.
    replace("'hps-", "'psn-v2-")
    if '"hps-' in text:
        replace('"hps-', '"psn-v2-')
    head = (HEAD_A + '<script src="./app/theme.js"></script>\n'
            '<link rel="stylesheet" href="./app/original-addon.css">\n'
            '<link rel="stylesheet" href="./app/version-switch.css">\n' + HEAD_B)
    # Theme must be set before CSS paint. The additive CSS does not replace core CSS.
    pos = text.lower().find('<style')
    if pos < 0:
        raise ValueError('No original style anchor.')
    text = text[:pos] + head + text[pos:]
    body = (BODY_A + '<script src="./app/original-addon.js"></script>\n'
            '<script src="./app/next-boot.js"></script>\n'
            '<script src="./app/version-switch.js" data-current-version="2"></script>\n' + BODY_B)
    pos = closing_offset(text, 'body')
    text = text[:pos] + body + text[pos:]
    recovered = text.replace(head, '', 1).replace(body, '', 1)
    for change in reversed(changes):
        if recovered.count(change['new']) != change['count']:
            raise AssertionError('Inverse patch count mismatch.')
        recovered = recovered.replace(change['new'], change['old'])
    if recovered != original or recovered.encode('utf-8') != raw:
        raise AssertionError('Lossless source recovery failed.')
    # Original HTML IDs remain exactly the same; new controls are separate nodes.
    ids = lambda s: re.findall(r'\bid\s*=\s*[\'"]([^\'"]+)[\'"]', s)
    if ids(original) != ids(text):
        raise AssertionError('Original control identifiers changed.')
    output = text.encode('utf-8')
    return output, {
        'original_sha256': digest(raw), 'output_sha256': digest(output),
        'original_bytes': len(raw), 'output_bytes': len(output),
        'inverse_patch_recovers_original_bytes': True,
        'original_control_identifiers_preserved': True,
        'edits': changes,
        'typed_note_compact_korean_supported': True,
        'typed_note_insertion_and_hand_assignment_changed': False,
        'audio_and_recognition_algorithms_changed': False,
        'full_responsive_preview_integrated': False,
    }

def build(source: Path, out: Path, *, verify_source: bool = True) -> dict:
    source, out = source.resolve(), out.resolve()
    if source == out or out.is_relative_to(source) or source.is_relative_to(out):
        raise ValueError('Output must be separate from the original checkout.')
    if out.exists():
        raise FileExistsError(f'Output exists; nothing overwritten: {out}')
    commit = validate_checkout(source) if verify_source else 'TEST-FIXTURE-NOT-UPSTREAM'
    before = {}
    for name in CONFIG['runtime_files']:
        file = source / name
        if not file.is_file() or file.is_symlink():
            raise ValueError(f'Missing/non-regular original runtime asset: {name}')
        before[name] = digest(file.read_bytes())
    patched, patch_report = patch_html((source / 'index.html').read_bytes())
    manifest = json.loads((source / 'manifest.webmanifest').read_text(encoding='utf-8'))
    manifest.update(name='우리집 연주실 2', short_name='연주실 2',
                    description='Piano Studio Next — 녹음·채보·편집·메트로놈. v2 초기 개발판.',
                    id='./', start_url='./', scope='./', display='standalone',
                    background_color='#11151F', theme_color='#11151F')
    inputs = patched + json.dumps(manifest, ensure_ascii=False).encode('utf-8')
    for file in sorted((ROOT / 'app').glob('*')):
        if file.is_file():
            inputs += file.read_bytes()
    build_id = VERSION + '-' + digest(inputs)[:12]
    try:
        out.mkdir(parents=True)
        for name in CONFIG['runtime_files']:
            shutil.copy2(source / name, out / name)
        (out / 'index.html').write_bytes(patched)
        shutil.copytree(ROOT / 'app', out / 'app', ignore=shutil.ignore_patterns('sw.js'))
        shutil.copytree(ROOT / 'preview', out / 'preview')
        (out / 'manifest.webmanifest').write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (out / 'sw.js').write_text((ROOT / 'app' / 'sw.js').read_text(encoding='utf-8')
                                  .replace('__BUILD_ID__', build_id), encoding='utf-8')
        (out / '.nojekyll').write_text('', encoding='utf-8')
        report = {
            'version': VERSION, 'build_id': build_id,
            'upstream_repository': CONFIG['repository'], 'upstream_commit': commit,
            'upstream_git_verified': verify_source, 'source_files': before,
            'html_patch': patch_report,
            'source_checkout_unchanged': all(digest((source/n).read_bytes()) == sha
                                           for n, sha in before.items()),
            'runtime_assets_byte_preserved': all(
                digest((out/n).read_bytes()) == before[n]
                for n in CONFIG['runtime_files']
                if n not in ('index.html', 'manifest.webmanifest', 'sw.js')),
            'storage_database': 'piano-studio-next-v2',
            'storage_key_prefix': 'psn-v2-',
            'note': 'Source-preservation/build checks, not an accuracy or physical-device test.'
        }
        if not report['source_checkout_unchanged'] or not report['runtime_assets_byte_preserved']:
            raise AssertionError('Source or original asset preservation failed.')
        (out / 'build-info.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        # Keep an identifiable original snapshot inside the artifact, not the served website.
        return report
    except Exception:
        # A partially built output must never be deployed. It contains only this build's files.
        if out.exists():
            shutil.rmtree(out)
        raise

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    report = build(args.upstream, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, AssertionError, subprocess.CalledProcessError) as exc:
        print(f'BUILD FAILED: {exc}', file=sys.stderr)
        raise SystemExit(1)
