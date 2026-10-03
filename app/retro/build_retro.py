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
def build_key():
 return hashlib.sha256(b''.join((HERE/n).read_bytes() for n in ['gme_bridge.cpp','build_retro.py','smoke_wasm.mjs'])).hexdigest()
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
