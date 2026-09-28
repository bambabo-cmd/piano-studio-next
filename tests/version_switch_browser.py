#!/usr/bin/env python3
"""Shared v1/v2 switcher tests using synthetic app HTML and a simulated IndexedDB transaction contract.
Uses set_content without network navigation. No actual upstream engine, microphone, Safari, or Pages deployment.
"""
from pathlib import Path
import argparse, json, shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--report',type=Path,required=True);p.add_argument('--screenshots',type=Path);args=p.parse_args()
    results=[]
    def check(name,value):
        results.append({'name':name,'pass':bool(value)})
        if not value:print('FAIL',name)
    css=(ROOT/'app/version-switch.css').read_text();js=(ROOT/'app/version-switch.js').read_text()
    def html(version):
        name='우리집 연주실'+(' 2' if version=='2' else '')
        dbname='piano-studio-next-v2' if version=='2' else 'home-piano-studio'
        return '''<!doctype html><html lang="ko" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
        :root{--paper:#f4f6fb;--panel:#fff;--ink:#1f2a44;--line:#dadfea;--accent:#3552d6;--muted:#5c6684}:root[data-theme=dark]{--paper:#11151f;--panel:#1a2030;--ink:#e7ebf5;--line:#2b3348;--accent:#8196ff;--muted:#98a1bc;color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:14px;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui}.wrap{max-width:1180px;margin:auto}.top{display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap;justify-content:space-between}h1{font-weight:600;font-size:30px;line-height:1.1;margin:0}button{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;min-height:44px;padding:6px 12px}.test-card{margin-top:20px;padding:20px;border:1px solid var(--line);border-radius:16px;background:var(--panel)}.test-card p{color:var(--muted)}[hidden]{display:none!important}
        </style><style>'''+css+'''</style></head><body><div class="wrap"><header class="top"><h1>'''+name+'''</h1></header><section class="test-card"><strong>버전 전환 버튼 검사용 화면</strong><p>실제 앱 전체를 실행한 화면이 아닙니다. 버튼 배치와 저장·이동 방어 동작을 검사합니다.</p><button id="recBtn">녹음</button> <button id="playBtn">재생</button> <button id="mpOpen">메트로놈</button></section><div id="overlay" hidden>처리 중</div></div><script>
        let recording=null;
        let project={id:'test-song',name:'edited song',bpm:100,tracks:[{notes:[{p:60,s:0,d:1,v:90,h:'L'}],audio:new Blob(['test-audio'],{type:'audio/webm'})}]};
        const DB={db:null};
        window.databaseReady=false;window.alerts=[];window.navEvents=[];
        window.alert=text=>alerts.push(text);
        addEventListener('piano-version-navigate',e=>{e.preventDefault();navEvents.push(e.detail)});
        document.getElementById('recBtn').onclick=()=>{recording=recording?null:{kind:'mic'};document.getElementById('recBtn').classList.toggle('recording',!!recording)};
        window.originalRecordHandler=document.getElementById('recBtn').onclick;
        window.mockStores=new Map([['projects',new Map()],['meta',new Map()]]);
        DB.db={transaction(names,mode){
          let aborted=false;const writes=[];const tx={
            abort(){aborted=true;if(tx.onabort)tx.onabort()},
            objectStore(name){return {
              put(value,key){const clone=structuredClone(value);writes.push([name,key===undefined?value.id:key,clone]);return {result:key}},
              get(key){const request={};setTimeout(()=>{request.result=structuredClone(mockStores.get(name).get(key));if(request.onsuccess)request.onsuccess()},0);return request}
            }}
          };
          setTimeout(()=>{if(aborted)return;for(const [name,key,value] of writes)mockStores.get(name).set(key,value);if(tx.oncomplete)tx.oncomplete()},0);
          return tx;
        }};
        window.databaseReady=true;
        window.readSaved=()=>new Promise((res,rej)=>{const q=DB.db.transaction('projects').objectStore('projects').get('test-song');q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)});
        </script><script data-current-version="'''+version+'''">'''+js+'''</script></body></html>'''
    if args.screenshots:args.screenshots.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
        for v in ['1','2']:
            for screen,w,h in [('phone_small',320,667),('iphone_portrait',390,844),('iphone_landscape',844,390),('ipad_portrait',820,1180),('ipad_landscape',1180,820),('laptop',1440,900)]:
                label='v'+v+'/'+screen
                ctx=browser.new_context(viewport={'width':w,'height':h});page=ctx.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.set_content(html(v))
                page.wait_for_function('databaseReady && !!document.getElementById("ps-version-switch")')
                nav=page.locator('#ps-version-switch');other='2' if v=='1' else '1';link=nav.locator('a')
                check(label+' current marker',nav.locator('[aria-current=page]').get_attribute('data-version')==v)
                check(label+' exact destination',link.get_attribute('href')=='https://bambabo-cmd.github.io/'+('piano-studio-next/' if v=='1' else 'piano-studio/'))
                check(label+' current cannot reload',nav.locator('[aria-current=page]').get_attribute('href') is None)
                for theme in ['dark','light']:
                    page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
                    check(label+'/'+theme+' bounds',nav.evaluate('(e)=>{let r=e.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth+.5 && r.top>=0}'))
                    check(label+'/'+theme+' page no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                page.evaluate('document.documentElement.dataset.theme="dark"')
                if args.screenshots and screen in ('iphone_portrait','laptop'):
                    page.screenshot(path=str(args.screenshots/(label.replace('/','_')+'.png')))
                page.locator('#recBtn').click();link.click()
                check(label+' recording blocks navigation',page.evaluate('navEvents.length===0 && alerts.at(-1).includes("녹음 중")'))
                page.locator('#recBtn').click();page.evaluate('document.getElementById("overlay").hidden=false');link.click()
                check(label+' processing blocks navigation',page.evaluate('navEvents.length===0 && alerts.at(-1).includes("분석")'))
                page.evaluate('document.getElementById("overlay").hidden=true');link.click();page.wait_for_function('navEvents.length===1')
                saved=page.evaluate('async()=>{const p=await readSaved();return {name:p.name,hand:p.tracks[0].notes[0].h,audio:await p.tracks[0].audio.text()}}')
                check(label+' simulated transaction finishes before navigation',saved=={'name':'edited song','hand':'L','audio':'test-audio'})
                check(label+' navigation event destination',page.evaluate('navEvents[0].version')==other)
                page.evaluate('window.txBefore=DB.db.transaction;DB.db.transaction=()=>{throw new Error("TEST QUOTA FAILURE")};project.name="must-not-be-lost"')
                link.click();page.wait_for_function('!document.getElementById("ps-version-switch").hasAttribute("aria-busy")')
                check(label+' save failure blocks navigation',page.evaluate('navEvents.length===1 && alerts.at(-1).includes("TEST QUOTA FAILURE")'))
                page.evaluate('DB.db.transaction=txBefore')
                check(label+' original record handler preserved',page.evaluate('document.getElementById("recBtn").onclick===originalRecordHandler'))
                page.add_script_tag(content=js)
                check(label+' duplicate script safe',page.locator('#ps-version-switch').count()==1)
                check(label+' no JavaScript errors',not errors)
                ctx.close()
        browser.close()
    report={'scope':'Synthetic app DOM and simulated IndexedDB transactions; navigation is intercepted. Real IndexedDB and network navigation were not tested. Not the actual upstream audio/AI engine or a physical device.','checks':results,'summary':{'total':len(results),'passed':sum(x['pass'] for x in results)}}
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(report['summary']);return 0 if all(x['pass'] for x in results) else 1
if __name__=='__main__':raise SystemExit(main())
