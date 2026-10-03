import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const dir=path.resolve(process.argv[2]);globalThis.require=createRequire(import.meta.url);globalThis.__dirname=dir;globalThis.__filename=path.join(dir,'gme-engine.mjs');
const {default:factory}=await import(pathToFileURL(path.join(dir,'gme-engine.mjs')));
const M=await factory({wasmBinary:fs.readFileSync(path.join(dir,'gme-engine.wasm'))});
const cmds=[0x50,0x80|0x0e,0x50,0x0f,0x50,0x90,0x61,0x44,0xac,0x50,0x9f,0x66];
const a=new Uint8Array(64+cmds.length),v=new DataView(a.buffer);a.set([0x56,0x67,0x6d,0x20]);v.setUint32(4,a.length-4,true);v.setUint32(8,0x150,true);v.setUint32(12,3579545,true);v.setUint32(0x18,44100,true);v.setUint32(0x34,12,true);a.set(cmds,64);
const ptr=M._malloc(a.length),out=M._malloc(2048*4);M.HEAPU8.set(a,ptr);
if(M._psn_open(ptr,a.length,32000)!==0)throw Error(M.UTF8ToString(M._psn_error()));
if(M._psn_voices()!==4)throw Error('WASM PSG voice count');
const results=[];for(const ch of [0,1]){if(M._psn_start(0,ch,1))throw Error('start');let energy=0;for(let i=0;i<8;i++){if(M._psn_render(out,2048))throw Error('render');for(let j=0;j<4096;j++)energy+=Math.abs(M.HEAP16[(out>>1)+j]);}results.push(energy);}
M._psn_close();M._free(ptr);M._free(out);if(!(results[0]>0&&results[1]===0))throw Error('WASM channel isolation: '+results);
fs.writeFileSync(path.join(dir,'wasm-smoke.json'),JSON.stringify({passed:true,actualWasm:true,syntheticVgm:true,voice0Energy:results[0],voice1Energy:results[1]},null,2));console.log('Actual WASM PSG channel isolation passed',results);
