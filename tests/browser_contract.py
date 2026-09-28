#!/usr/bin/env python3
"""Local DOM contract tests: synthetic original, in-memory Storage, no navigation.
Requires Playwright + Chromium. Not a real original-engine, microphone, DB, or PWA test.
"""
from pathlib import Path
import argparse, json, shutil, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_build import FIXTURE, build_site, ROOT

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    report={'scope':'Synthetic DOM/handler contract with in-memory localStorage simulation. No network navigation, upstream engine, real IndexedDB, browser service worker, microphone, or physical device execution.','checks':[]}
    def check(name,ok):
        report['checks'].append({'name':name,'pass':bool(ok)})
        if not ok:print('FAIL',name)
    html=build_site.patch_html(FIXTURE)[0].decode()
    for name in ['theme.js','original-addon.js','next-boot.js']:
        html=html.replace(f'<script src="./app/{name}"></script>', '<script>\n'+(ROOT/'app'/name).read_text()+'\n</script>')
    html=html.replace('<link rel="stylesheet" href="./app/original-addon.css">','<style>'+(ROOT/'app'/'original-addon.css').read_text()+'</style>')
    html=html.replace('<script src="./app/version-switch.js" data-current-version="2"></script>', '<script data-current-version="2">'+(ROOT/'app/version-switch.js').read_text()+'</script>')
    html=html.replace('<link rel="stylesheet" href="./app/version-switch.css">','<style>'+(ROOT/'app/version-switch.css').read_text()+'</style>')
    storage='''<script>window.memoryStorage=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memoryStorage.has(k)?memoryStorage.get(k):null,setItem:(k,v)=>memoryStorage.set(k,String(v)),removeItem:k=>memoryStorage.delete(k)}});</script>'''
    html=html.replace('<head>','<head>'+storage,1)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
        for name,w,h in [('phone_portrait',390,844),('phone_landscape',844,390),('tablet_portrait',820,1180),('tablet_landscape',1180,820),('laptop',1440,900)]:
            ctx=browser.new_context(viewport={'width':w,'height':h},color_scheme='light')
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(html);page.wait_for_function('window.__PianoOriginalAddon && window.__PianoOriginalAddon.ready')
            check(name+': dark is default with light system',page.evaluate('PianoTheme.get().choice==="dark" && document.documentElement.dataset.theme==="dark"'))
            check(name+': original DOM and handlers unchanged',page.evaluate('Object.entries(originalHandlers).every(([id,h])=>document.getElementById(id)===originalElements[id]&&document.getElementById(id).onclick===h)'))
            check(name+': dock inside viewport',page.locator('#ps-tools-dock').evaluate('(e)=>{let r=e.getBoundingClientRect();return r.left>=-.5&&r.right<=innerWidth+.5&&r.bottom<=innerHeight+.5}'))
            project=page.evaluate('JSON.stringify(testProject)')
            palette=page.evaluate('counts.palette');page.locator('#ps-theme-select').select_option('light')
            check(name+': theme refreshes original canvas palette',page.evaluate('counts.palette')>palette)
            page.locator('#ps-theme-select').select_option('system');page.emulate_media(color_scheme='dark');page.wait_for_timeout(100)
            check(name+': system theme follows changed preference',page.evaluate('document.documentElement.dataset.theme==="dark"'))
            page.locator('[data-ps-action=metro]').click();page.wait_for_timeout(30)
            check(name+': independent start invokes original once',page.evaluate('counts.open===1&&counts.start===1&&document.getElementById("metroPanel").hidden&&document.getElementById("mpOpen").classList.contains("running")'))
            page.locator('#ps-theme-select').select_option('light')
            check(name+': changing theme keeps metronome running',page.evaluate('counts.start===1&&document.getElementById("mpOpen").classList.contains("running")'))
            page.locator('[data-ps-action=metro]').click();page.wait_for_timeout(30)
            check(name+': stop does not reload metronome',page.evaluate('counts.open===1&&counts.start===2&&!document.getElementById("mpOpen").classList.contains("running")'))
            for action in ['record','play','sheet']:page.locator('[data-ps-action='+action+']').click()
            check(name+': primary actions forwarded once',page.evaluate('counts.record===1&&counts.play===1&&counts.sheet===1'))
            page.locator('#exMidi').click()
            check(name+': original export handler retained',page.evaluate('counts.export===1'))
            check(name+': project data unchanged',page.evaluate('JSON.stringify(testProject)')==project)
            page.evaluate('localStorage.setItem("hps-metro","V1-SENTINEL");storeSetting("V2-ONLY")')
            check(name+': simulated v1 settings untouched',page.evaluate('localStorage.getItem("hps-metro")==="V1-SENTINEL"&&localStorage.getItem("psn-v2-metro")==="V2-ONLY"'))
            check(name+': theme uses new storage key',page.evaluate('localStorage.getItem("piano-studio-next-theme-v2")==="light"'))
            check(name+': no script errors',not errors)
            ctx.close()
        browser.close()
    report['summary']={'total':len(report['checks']),'passed':sum(c['pass'] for c in report['checks'])}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report['summary'])
    return 0 if all(c['pass'] for c in report['checks']) else 1
if __name__=='__main__':raise SystemExit(main())
