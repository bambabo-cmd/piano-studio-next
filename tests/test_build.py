"""Unit tests with a clearly marked synthetic original. These are NOT engine E2E tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_site', ROOT/'tools'/'build_site.py')
build_site=importlib.util.module_from_spec(spec);spec.loader.exec_module(build_site)
FIXTURE='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#eee"><title>우리집 연주실</title><meta name="apple-mobile-web-app-title" content="우리집 연주실"><style>
:root{--paper:#f4f6fb;--panel:white;--ink:#223;--line:#dde;--rec:#c34;--accent:#56d;--muted:#667}:root[data-theme=dark]{--paper:#11151f;--panel:#1a2030;--ink:#eef;--line:#334;--muted:#abc}*{box-sizing:border-box}body{background:var(--paper);color:var(--ink);margin:0;font:14px system-ui}.top{display:flex;flex-wrap:wrap;padding:12px;gap:10px}button{font:inherit;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:10px;min-height:44px}select{font:inherit;color:inherit;background:var(--panel)}[hidden]{display:none!important}
</style></head><body><header class="top"><h1>우리집 연주실</h1><button id="mpOpen">메트로놈</button></header>
<p>SYNTHETIC TEST FIXTURE — NOT THE ORIGINAL APP</p>
<button id="recBtn">녹음</button><button id="playBtn">재생</button><button id="shOpen">악보</button><button id="exMidi">MIDI</button><button id="exJson">JSON</button><button id="imJson">불러오기</button><button id="newTrackBtn">빈 트랙</button><button id="typeBtn">타이핑</button><div id="tracks"></div><canvas id="roll"></canvas>
<div id="metroPanel" hidden><button id="mpClose">닫기</button><button id="mpStart">시작</button></div><script>
window.testProject={tracks:[{id:1,notes:[{p:60,s:0,d:1,h:'L'}]}]};
window.counts={record:0,play:0,sheet:0,open:0,start:0,export:0,palette:0};
const q=id=>document.getElementById(id);
// Verify that export format identifiers are NOT renamed along with the database.
const exportFormat='home-piano-studio';
function openDatabase(){return indexedDB.open('home-piano-studio',1);}
function storeSetting(v){localStorage.setItem('hps-metro',v);localStorage.setItem('hps-'+'deck-folded','1');}
function mpWire(){q('mpOpen').onclick=()=>{counts.open++;q('metroPanel').hidden=false;};q('mpClose').onclick=()=>q('metroPanel').hidden=true;q('mpStart').onclick=()=>{counts.start++;q('mpOpen').classList.toggle('running');q('mpStart').textContent=q('mpOpen').classList.contains('running')?'멈추기':'시작';};}
function readColors(){counts.palette++;}function drawRoll(){}
mpWire();q('recBtn').onclick=()=>{counts.record++;q('recBtn').classList.toggle('recording');};q('playBtn').onclick=()=>counts.play++;q('shOpen').onclick=()=>counts.sheet++;q('exMidi').onclick=()=>counts.export++;
window.originalHandlers=Object.fromEntries(['recBtn','playBtn','shOpen','mpOpen','mpStart','mpClose','exMidi'].map(id=>[id,q(id).onclick]));window.originalElements=Object.fromEntries(Object.keys(originalHandlers).map(id=>[id,q(id)]));
</script></body></html>'''.encode('utf-8')

FIXTURE=FIXTURE.replace(b'</script>',(ROOT/'tests/manual_entry_upstream_excerpt.js').read_bytes()+b'</script>',1)

def make_source(path):
    path.mkdir()
    for name in build_site.CONFIG['runtime_files']:
        (path/name).write_bytes(b'SYNTHETIC ASSET; NOT FOR DEPLOYMENT')
    (path/'index.html').write_bytes(FIXTURE)
    (path/'manifest.webmanifest').write_text(json.dumps({'name':'original','icons':[]}),encoding='utf-8')

class BuildTests(unittest.TestCase):
    def test_01_patch_is_reversible(self):
        data, report=build_site.patch_html(FIXTURE)
        self.assertTrue(report['inverse_patch_recovers_original_bytes'])
        self.assertTrue(report['original_control_identifiers_preserved'])
        recovered=data.decode()
        import re
        for a,b in [(build_site.HEAD_A,build_site.HEAD_B),(build_site.BODY_A,build_site.BODY_B)]:
            recovered=re.sub(re.escape(a)+'.*?'+re.escape(b),'',recovered,flags=re.S)
        for edit in reversed(report['edits']):recovered=recovered.replace(edit['new'],edit['old'])
        self.assertEqual(recovered.encode(),FIXTURE)
    def test_02_namespace_separates_database_not_export(self):
        text=build_site.patch_html(FIXTURE)[0].decode()
        self.assertIn("indexedDB.open('piano-studio-next-v2',1)",text)
        self.assertIn("const exportFormat='home-piano-studio';",text)
        self.assertNotIn("'hps-",text)
        self.assertIn("'psn-v2-'+'deck-folded'",text)
    def test_03_double_patch_rejected(self):
        with self.assertRaises(ValueError):build_site.patch_html(build_site.patch_html(FIXTURE)[0])
    def test_04_missing_control_rejected(self):
        with self.assertRaises(ValueError):build_site.patch_html(FIXTURE.replace(b'id="recBtn"',b'id="missing"'))
    def test_05_preview_cannot_be_used_as_original(self):
        with self.assertRaises(ValueError):build_site.patch_html((ROOT/'preview'/'index.html').read_bytes())
    def test_06_wrong_database_anchor_rejected(self):
        with self.assertRaises(ValueError):build_site.patch_html(FIXTURE.replace(b'home-piano-studio',b'other-app'))
    def test_07_full_fixture_build_preserves_source_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';out=Path(tmp)/'output';make_source(src)
            report=build_site.build(src,out,verify_source=False)
            self.assertTrue(report['source_checkout_unchanged'])
            self.assertTrue(report['runtime_assets_byte_preserved'])
            self.assertEqual((src/'index.html').read_bytes(),FIXTURE)
            self.assertFalse(report['upstream_git_verified'])
            self.assertEqual(report['upstream_commit'],'TEST-FIXTURE-NOT-UPSTREAM')
            self.assertTrue((out/'app'/'next-boot.js').is_file())
            self.assertTrue((out/'preview'/'index.html').is_file())
            self.assertNotIn('__BUILD_ID__',(out/'sw.js').read_text())
    def test_08_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';out=Path(tmp)/'output';make_source(src);out.mkdir()
            with self.assertRaises(FileExistsError):build_site.build(src,out,verify_source=False)
    def test_09_reject_source_inside_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';make_source(src)
            with self.assertRaises(ValueError):build_site.build(src,src/'dist',verify_source=False)
    def test_10_missing_runtime_asset_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';out=Path(tmp)/'output';make_source(src);(src/'bp.bundle.js').unlink()
            with self.assertRaises(ValueError):build_site.build(src,out,verify_source=False)
            self.assertFalse(out.exists())
    def test_11_git_verification_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';make_source(src)
            with self.assertRaises(Exception):build_site.build(src,Path(tmp)/'out')
    def test_12_manifest_has_separate_name_and_relative_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';out=Path(tmp)/'output';make_source(src)
            build_site.build(src,out,verify_source=False)
            m=json.loads((out/'manifest.webmanifest').read_text())
            self.assertEqual(m['name'],'우리집 연주실 2');self.assertEqual(m['scope'],'./')
            self.assertEqual(m['start_url'],'./');self.assertEqual(m['id'],'./')
    def test_13_required_script_references_are_relative(self):
        html=build_site.patch_html(FIXTURE)[0].decode()
        for name in ['theme.js','original-addon.js','next-boot.js']:
            self.assertIn('./app/'+name,html)
    def test_14_wrong_encoding_rejected(self):
        with self.assertRaises(UnicodeDecodeError):build_site.patch_html(b'\xff\xfe'+FIXTURE)
    def test_15_locked_revision_is_full_hash(self):
        self.assertRegex(build_site.CONFIG['commit'],r'^[0-9a-f]{40}$')
        self.assertNotEqual(build_site.CONFIG['commit'],'main')


class NavigationBuildTests(unittest.TestCase):
    def test_real_body_anchor_ignores_print_template(self):
        fixture=FIXTURE.replace(b'window.testProject=', b'const printHTML="<html><head></head><body>print</body></html>";window.testProject=',1)
        output,report=build_site.patch_html(fixture)
        self.assertTrue(report['inverse_patch_recovers_original_bytes'])
        self.assertIn(b'<body>print</body>',output)
    def test_version_switch_config_and_assets(self):
        output,_=build_site.patch_html(FIXTURE)
        self.assertIn(b'data-current-version="2"',output)
        self.assertIn(b'./app/version-switch.css',output)
        self.assertIn('version-switch.js',(ROOT/'app/sw.js').read_text())
    def test_nav_does_not_rewire_recording(self):
        output,_=build_site.patch_html(FIXTURE)
        self.assertEqual(FIXTURE.count(b"q('recBtn').onclick="), output.count(b"q('recBtn').onclick="))

if __name__=='__main__':unittest.main()
