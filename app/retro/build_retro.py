#!/usr/bin/env python3
"""Build a small GME WASM worker engine during the existing Pages build.
Pinned library source, no downloaded game music, no runtime CORS dependency.
No sudo and no changes to the existing Pages workflow/settings are needed.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, tarfile, urllib.request, time, zipfile
HERE=Path(__file__).resolve().parent
GME_COMMIT='dd3182a8bdae3ff761438632aace418fbcaed439'
SDK_VERSION='3.1.64'
EXPORTS=['malloc','free','psn_error','psn_close','psn_open','psn_tracks','psn_voices','psn_voice_name','psn_info','psn_info_text','psn_info_ms','psn_warning','psn_start','psn_render']
def run(args,**kw):
 print('+',' '.join(map(str,args)),flush=True);subprocess.run(list(map(str,args)),check=True,**kw)
def fetch(url,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PianoStudioNext-build/21'}),timeout=60) as response, tmp.open('wb') as out:shutil.copyfileobj(response,out)
   tmp.replace(path);return
  except Exception:
   tmp.unlink(missing_ok=True)
   if attempt==2:raise
   time.sleep(2+attempt)
def extract(archive,dest):
 dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive) as tar:
  for m in tar.getmembers():
   p=(dest/m.name).resolve()
   if not p.is_relative_to(dest.resolve()) or m.issym() or m.islnk():raise ValueError('Unsafe source archive path')
  # Paths and links were validated above, also works on Python 3.10.
  for m in tar.getmembers():
   if not (m.isfile() or m.isdir()):raise ValueError('Unexpected archive entry')
  tar.extractall(dest)
def fix_browser_loader(file):
 # Emscripten 3.1.64 ENVIRONMENT=worker,node with EXPORT_ES6 emits a Node-only
 # static import. Node smoke alone cannot detect this browser resolution failure.
 old = "import { createRequire } from 'module';\nconst require = createRequire(import.meta.url);"
 new = "// Piano Studio alpha.25: Node built-ins must not be statically imported by browser Workers.\nlet require;\nif (typeof process === 'object' && process.versions && process.versions.node) {\n  const { createRequire } = await import('node:module');\n  require = createRequire(import.meta.url);\n}"
 text=Path(file).read_text(encoding='utf-8')
 if old in text:
  if text.count(old)!=1:raise ValueError('Ambiguous ESM Node preamble')
  Path(file).write_text(text.replace(old,new,1),encoding='utf-8')
 elif "from 'module'" in text or 'from "module"' in text:
  raise ValueError('Unhandled static Node dependency in browser worker module')

def build_key():
 return hashlib.sha256(b''.join((HERE/n).read_bytes() for n in ['gme_bridge.cpp','build_retro.py','smoke_wasm.mjs'])).hexdigest()
# alpha.25: ship the successful app-owned build and its complete corresponding sources.
# A corrupt bundled engine is a hard error, not an excuse to publish broken assets.
BUNDLED_FILES = {'gme-engine.mjs': 'afef4b69be4bca36a4742b5b38904a73ff99e6a1902257eecea1f7dccd86df02', 'gme-engine.wasm': '7592b9dac0e4869ebc8eda165d9f4cb8814d44baf473441bf42347f7a070e4a6', 'gme-corresponding-source.zip': 'bb1e8c666896009926e3a7b5a372ef9f9d13ba7ff8249fcdc3868904b882056d', 'gme-license.txt': 'd2efc89fbb7533572a472d34e07964951810a3a4f8d3159ecc2dcaa1452c5c26', 'gme-readme.txt': 'ebb2ccb9a60e178b24cbd815d187cbfd6d30fbda04cfc09346bbaf84e6b936bc'}
BUNDLED_BRIDGE_SHA256 = '437bbb2857d6461f11e92077bb62560740d6de825f2dab41fabd3bc29e0305ab'
def reuse_bundled(out):
 if not (HERE/'bundled-engine.json').exists():return None
 report=json.loads((HERE/'bundled-engine.json').read_text(encoding='utf-8'))
 if report.get('gme_commit')!=GME_COMMIT:raise ValueError('Bundled source revision mismatch')
 if hashlib.sha256((HERE/'gme_bridge.cpp').read_bytes()).hexdigest()!=BUNDLED_BRIDGE_SHA256:
  raise ValueError('GME bridge changed: rebuild the engine and update pinned bundle checksums')
 for n,sha in BUNDLED_FILES.items():
  p=HERE/n
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
   raise ValueError('Bundled engine integrity mismatch: '+n)
 for n in BUNDLED_FILES:
  if (HERE/n).resolve()!=(out/n).resolve():shutil.copy2(HERE/n,out/n)
 run(['node',HERE/'smoke_wasm.mjs',str(out.resolve())])
 report.update(source_build_key=report['build_key'],build_key=build_key(),
  loader_patch='conditional node:module import; browser Workers do not load Node built-ins',
  method='chip-channel PCM, not sequence-note extraction',
  reused_bundled_engine=True,origin_repository='bambabo-cmd/piano-studio-next',
  origin_run=37095556195,origin_artifact=11264765093,
  files=BUNDLED_FILES,local_wasm_execution_check=True)
 (out/'engine-build.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Verified bundled GME WASM; no compiler or source download needed.',flush=True)
 return report

def reuse_published(out):
 # Only this app's previously validated public deployment, never user-provided URLs.
 base='https://bambabo-cmd.github.io/piano-studio-next/app/retro/'
 names=['gme-engine.mjs','gme-engine.wasm','gme-corresponding-source.zip','gme-license.txt','gme-readme.txt']
 try:
  with urllib.request.urlopen(base+'engine-build.json',timeout=8) as r: report=json.loads(r.read(64000))
  if report.get('build_key')!=build_key() or report.get('gme_commit')!=GME_COMMIT:return None
  for n in names:
   data=urllib.request.urlopen(base+n,timeout=25).read(16*1024*1024)
   if hashlib.sha256(data).hexdigest()!=report.get('files',{}).get(n):raise ValueError('Cached engine integrity mismatch')
   (out/n).write_bytes(data)
  run(['node',HERE/'smoke_wasm.mjs',str(out.resolve())])
  (out/'engine-build.json').write_text(json.dumps(report,indent=2)+'\n')
  print('Reused existing identical engine; actual WASM smoke test passed.',flush=True)
  return report
 except Exception as e:
  print('No reusable engine; building pinned source: '+str(e),flush=True)
  for n in names:(out/n).unlink(missing_ok=True)
  return None
def prepare(out,work=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);work=Path(work or os.environ.get('RUNNER_TEMP','/tmp'))/'piano-retro-build21';work.mkdir(parents=True,exist_ok=True)
 cached=reuse_bundled(out)
 if cached:return cached
 cached=reuse_published(out)
 if cached:return cached
 env=dict(os.environ);emcc=shutil.which('emcc');emcmake=shutil.which('emcmake')
 if not emcc:
  sdk=work/'emsdk'
  if not (sdk/'emsdk.py').exists():
   arc=work/'sdk.tar.gz';fetch('https://github.com/emscripten-core/emsdk/archive/refs/tags/'+SDK_VERSION+'.tar.gz',arc);tmp=work/'sdk-extracted';extract(arc,tmp);shutil.move(str(next(tmp.iterdir())),sdk)
  run(['python3',sdk/'emsdk.py','install',SDK_VERSION]);run(['python3',sdk/'emsdk.py','activate',SDK_VERSION])
  setup=subprocess.check_output(['bash','-c','source "$1/emsdk_env.sh" >/dev/null 2>&1; env -0','bash',str(sdk)])
  for entry in setup.split(b'\0'):
   if b'=' in entry:
    k,v=entry.split(b'=',1);env[k.decode()]=v.decode()
  emcc=str(sdk/'upstream/emscripten/emcc');emcmake=str(sdk/'upstream/emscripten/emcmake')
 source=work/'gme'
 if not (source/'gme/gme.h').exists():
  arc=work/'gme.tar.gz';fetch('https://github.com/libgme/game-music-emu/archive/'+GME_COMMIT+'.tar.gz',arc);tmp=work/'gme-extracted';extract(arc,tmp);shutil.move(str(next(tmp.iterdir())),source)
 build=work/'build';run([emcmake,'cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DGME_BUILD_SHARED=OFF','-DGME_BUILD_STATIC=ON','-DGME_ZLIB=OFF','-DGME_BUILD_TESTING=OFF','-DGME_BUILD_EXAMPLES=OFF','-DBUILD_TESTING=OFF','-DGME_YM2612_EMU=Nuked'],env=env)
 run(['cmake','--build',build,'--parallel','2'],env=env)
 libs=list(build.rglob('libgme.a'))
 if len(libs)!=1:raise RuntimeError('Expected one libgme.a')
 compiler=str(Path(emcc).with_name('em++'))
 run([compiler,'-I'+str(source/'gme'),HERE/'gme_bridge.cpp',libs[0],'-O2','-std=c++11','-s','MODULARIZE=1','-s','EXPORT_NAME=PianoGME','-s','EXPORT_ES6=1','-s','ENVIRONMENT=worker,node','-s','ALLOW_MEMORY_GROWTH=1','-s','INITIAL_MEMORY=16777216','-s','MAXIMUM_MEMORY=134217728','-s','FILESYSTEM=0','-s','EXPORTED_FUNCTIONS='+json.dumps(['_'+n for n in EXPORTS]),'-s','EXPORTED_RUNTIME_METHODS=["UTF8ToString","HEAPU8","HEAP16"]','-o',out/'gme-engine.mjs'],env=env)
 fix_browser_loader(out/'gme-engine.mjs')
 # LGPL corresponding sources + wrapper/build instructions; replace/relink the library freely.
 with zipfile.ZipFile(out/'gme-corresponding-source.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in source.rglob('*'):
   if p.is_file() and (p.relative_to(source).parts[0] in ['gme','cmake'] or p.name in ['CMakeLists.txt','license.txt','license.gpl2.txt','readme.txt','gme.txt']):z.write(p,'game-music-emu/'+str(p.relative_to(source)))
  for name in ['gme_bridge.cpp','build_retro.py','smoke_wasm.mjs','README_KO.md']:z.write(HERE/name,'piano-wrapper/'+name)
 for license in ['license.txt','readme.txt']:shutil.copy2(source/license,out/('gme-'+license))
 wasm=(out/'gme-engine.wasm').read_bytes()
 if not wasm.startswith(b'\0asm') or len(wasm)<50000:raise ValueError('WASM build not valid')
 report={'gme_commit':GME_COMMIT,'build_key':build_key(),'emsdk_requested':SDK_VERSION,'compiler_version':subprocess.check_output([emcc,'--version'],env=env,text=True).splitlines()[0],'engine_sha256':hashlib.sha256(wasm).hexdigest(),'wasm_bytes':len(wasm),'exports':EXPORTS,'formats':['SPC','NSF','NSFE','GBS','HES','VGM','VGZ'],'method':'chip-channel PCM, not sequence-note extraction'}
 report['files']={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['gme-engine.mjs','gme-engine.wasm','gme-corresponding-source.zip','gme-license.txt','gme-readme.txt']}
 (out/'engine-build.json').write_text(json.dumps(report,indent=2)+'\n')
 # Run the built WebAssembly under Node on a tiny deliberately generated VGM.
 # This gate runs in GitHub, where the SDK/engine are actually available.
 run(['node',HERE/'smoke_wasm.mjs',str(out.resolve())],env=env)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--work',type=Path);a=p.parse_args();prepare(a.output,a.work)
