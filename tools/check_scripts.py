#!/usr/bin/env python3
"""Run node --check on external and inline JavaScript; no dependency installation."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess, sys, tempfile

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts=[]; self.active=None
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs=dict(attrs)
            self.active = None if 'src' in attrs or attrs.get('type','') not in ('','text/javascript','application/javascript','module') else []
    def handle_data(self, data):
        if self.active is not None: self.active.append(data)
    def handle_endtag(self, tag):
        if tag == 'script' and self.active is not None:
            self.scripts.append(''.join(self.active)); self.active=None

def check(path):
    total=0
    for p in sorted(path.rglob('*.js')):
        subprocess.run(['node','--check',str(p)],check=True);total+=1
    for p in sorted(path.rglob('*.html')):
        parser=Scripts();parser.feed(p.read_text(encoding='utf-8'))
        for script in parser.scripts:
            with tempfile.TemporaryDirectory() as tmp:
                f=Path(tmp)/'inline.js';f.write_text(script,encoding='utf-8')
                subprocess.run(['node','--check',str(f)],check=True);total+=1
    print(f'JavaScript syntax checks passed: {total}')
    return total
if __name__=='__main__': check(Path(sys.argv[1] if len(sys.argv)>1 else 'dist'))
