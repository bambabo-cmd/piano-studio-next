"""Parser tests against the retrieved original manual-entry excerpt.
No AI, actual microphone, full original app or physical-device claim.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
HERE=Path(__file__).resolve().parent
PATCH=(HERE.parent/'tools'/'typed_note_patch.py') if (HERE.parent/'tools'/'typed_note_patch.py').is_file() else HERE/'typed_note_patch.py'
spec=importlib.util.spec_from_file_location('tested_typing_patch',PATCH)
patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
ORIGINAL=(HERE/'manual_entry_upstream_excerpt.js').read_text(encoding='utf-8')

class TypingTests(unittest.TestCase):
    def test_reviewed_anchors_are_unique_and_reversible(self):
        new,edits=patch.apply(ORIGINAL)
        self.assertEqual(len(edits),3)
        for edit in reversed(edits): new=new.replace(edit['new'],edit['old'],1)
        self.assertEqual(new,ORIGINAL)
    def test_changed_source_fails_closed(self):
        with self.assertRaises(ValueError): patch.apply(ORIGINAL.replace('function parseNoteText(', 'function anotherParser('))
    def test_duplicate_source_fails_closed(self):
        with self.assertRaises(ValueError): patch.apply(ORIGINAL+'\n'+ORIGINAL)
    def test_double_patch_fails_closed(self):
        with self.assertRaises(ValueError): patch.apply(patch.apply(ORIGINAL)[0])
    def test_only_lexer_and_help_change_not_insertion(self):
        new,_=patch.apply(ORIGINAL)
        start=ORIGINAL.index('  for(const raw of toks)')
        end=ORIGINAL.index('function openTypeEntry(')
        self.assertIn(ORIGINAL[start:end],new)
        start=ORIGINAL.index('  o.onclick=')
        self.assertTrue(new.endswith(ORIGINAL[start:]))
    def test_node_parser_equivalence(self):
        new,_=patch.apply(ORIGINAL)
        payload=json.dumps({'old':ORIGINAL,'new':new},ensure_ascii=False)
        code=r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const src=JSON.parse(fs.readFileSync(0,'utf8'));
function load(source){const c=vm.createContext({clamp:(x,a,b)=>Math.max(a,Math.min(b,x))});vm.runInContext(source,c);return (s,b=.5)=>JSON.parse(JSON.stringify(c.parseNoteText(s,b)));}
const old=load(src.old),fresh=load(src.new);
let assertions=0;
function equal(a,b){assert.deepEqual(a,b);assertions++;}
function ok(v){assert.ok(v);assertions++;}
equal(old('도도솔솔').bad,['도도솔솔']);
equal(fresh('도도솔솔'),old('도 도 솔 솔'));
equal(fresh('도도솔솔라라솔-파파미미레레도-'),old('도 도 솔 솔 라 라 솔- 파 파 미 미 레 레 도-'));
equal(fresh('도도솔솔').notes.map(n=>n.p),[60,60,67,67]);
equal(fresh('도미솔').notes.map(n=>n.p),[60,64,67]);
equal(fresh('도#레♭쉼미/파-솔5라^시v'),old('도# 레♭ 쉼 미/ 파- 솔5 라^ 시v'));
equal(fresh('도4레5미3파^^솔vv라4^-//시2--'),old('도4 레5 미3 파^^ 솔vv 라4^-// 시2--'));
equal(fresh('도_레.미r파R솔쉼/라'),old('도 _ 레 . 미 r 파 R 솔 쉼/ 라'));
equal(fresh('도,도，솔\n솔\t라 라'),old('도 도 솔 솔 라 라'));
// Protect existing English flat-b interpretation and explicit spacing.
for(const s of ['c d e f g a b','ab bb Cb4 A#4 F♯5','C4 D4 E4','abc','ccgg','c도','도c','r R . _','쉼/ 쉼-- _- R/']) equal(fresh(s),old(s));
for(const s of ['도오','도레?미','도레!!!미','도레<script>미','도10레','도##레','안녕하세요','솔직','도움말','도레♮미','도레쉼//미','도레미/--']) ok(fresh(s).bad.length>0);
for(const s of ['', '   ', ',，\n']) equal(fresh(s),old(s));
// All legacy single tokens from a bounded grammar remain byte-for-byte semantic equivalents.
const roots=['도','레','미','파','솔','라','시','c','D','e','F','g','a','B'];
for(const root of roots)for(const accidental of ['','#','♯','b','♭'])for(const oct of ['','3','4','5'])for(const mod of ['','^','v','^v','vv'])for(const len of ['','-','--','/','//','-/']){
 const s=root+accidental+oct+mod+len;equal(fresh(s),old(s));
}
// Deterministic random compact Korean sequences; compare with spaced original.
let seed=9728;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;}
const kr=['도','레','미','파','솔','라','시'];const acc=['','#','♯','b','♭'];const octave=['','3','4','5'];const mods=['','^','v','^v'];const lens=['','-','--','/','//','-/'];
for(let i=0;i<1000;i++){
 const items=[];for(let j=0,n=2+rand(20);j<n;j++)items.push(rand(7)===0?['쉼','쉼/','쉼--','_','.','r','R/'][rand(7)]:kr[rand(7)]+acc[rand(5)]+octave[rand(4)]+mods[rand(4)]+lens[rand(6)]);
 const base=[.25,.5,1,2][rand(4)];equal(fresh(items.join(''),base),old(items.join(' '),base));
}
console.log(JSON.stringify({passed:true,assertions,random_compact_sequences:1000,scope:'actual parser excerpt; not full app or physical-device test'}));
'''
        done=subprocess.run(['node','-e',code],input=payload,text=True,capture_output=True,check=True)
        report=json.loads(done.stdout)
        self.assertTrue(report['passed'])
        self.assertGreater(report['assertions'],9000)
        print('PARSER_RESULT '+json.dumps(report,ensure_ascii=False))
if __name__=='__main__':unittest.main()
