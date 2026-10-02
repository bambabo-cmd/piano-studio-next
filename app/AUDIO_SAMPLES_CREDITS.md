# 우리집 연주실 2 — 음원 출처·이용 조건 alpha.16

## 이번 추가: FluidR3 General MIDI 128 음색

- SoundFont: **FluidR3_GM**, Frank Wen and Fluid SoundFont contributors.
- Browser audio conversion/collection: **Benjamin Gleitzman and MIDI.js Soundfonts contributors**.
- Collection: https://github.com/gleitz/midi-js-soundfonts
- Fixed revision: `044fab8e1456bfafc5776e86dfd6bb8697149aef`.
- Exact catalogue: https://github.com/gleitz/midi-js-soundfonts/blob/044fab8e1456bfafc5776e86dfd6bb8697149aef/FluidR3_GM/names.json
- Collection licensing statement: https://github.com/gleitz/midi-js-soundfonts/blob/044fab8e1456bfafc5776e86dfd6bb8697149aef/README.md
- Audio: **Creative Commons Attribution 3.0 United States (CC BY 3.0 US)**, as linked by the collection: https://creativecommons.org/licenses/by/3.0/us/
- The audio license is not replaced by the repository's MIT code license.

The app adds Korean names, family and app-version metadata, and plays the collection's pre-rendered MP3 notes through its Web Audio player. It does **not** implement a full SoundFont/SF2 renderer or include MIDI.js scripts. No external JavaScript from the sample repository is executed.

Needed notes are fetched from the pinned revision through jsDelivr, with the matching raw.githubusercontent.com URL as a fallback. The upload ZIP contains player code and this attribution, not all external MP3s or the SF2 file. First-time loading requires an Internet connection; cache survival is browser-dependent.

App adaptations: time scheduling, MIDI note/velocity application, playback-rate adjustment when needed, a simple filter/envelope, and a crossfaded sustain loop in a private buffer copy for sufficiently long sustained notes. Original files are not rewritten. FluidR3 files do not receive the older collection's per-note level normalization, so their relative input levels remain intact before the common note gain. The full original SoundFont velocity layers, modulators, controller programming, release samples and resonances are not reproduced by this simplified MP3 player. The audio may therefore differ from the SF2 played through FluidSynth/BASSMIDI.

These are 128 **presets/timbres**, including electronic and sound-effect presets, not 128 distinct acoustic instruments. This catalogue does not include a full General MIDI channel-10 drum-kit engine, sung lyrics, sound-source separation, MT-32 emulation, or arbitrary user SF2 loading.

Attribution does not imply endorsement by any creator. Keep this notice and in-app source links when redistributing the app. When distributing adapted source samples, retain the required attribution/license and indicate changes.

## App version labels

- `기존 v1`: 16 original generated sounds, preserved for existing songs.
- `v2 α11 추가`: 20 note-recording instruments already included since alpha.11.
- `v2 α16 추가 · FluidR3`: 128 presets added in this update.

These labels are the time of inclusion in **this app**, not the library's publication date, sound quality ranking, or a claim that an old sound has become obsolete.

## Verification boundary, alpha.16

The 128-program catalogue, pinned repository revision and representative MP3 resource paths were checked against upstream. Actual downloadable piano C4 / woodblock C4 / electric piano Db4 resources were confirmed through GitHub. The runtime environment could not download external audio into the browser: decoding/scheduling tests instead use explicit generated WAV responses at these addresses. **Actual FluidR3 timbre, live CDN delivery and physical speaker/Safari playback were not auditioned or certified.** Test audio and test response routing are absent from the upload file.

---

## Preserved credits for the previous 20-instrument collection

The following original attribution remains applicable. Its verification statement describes the previous work and must be read together with the alpha.16 statement above.

# Instrument sample credits — Piano Studio Next alpha.11

## Source collection and license

**tonejs-instruments**, assembled and edited by **Nicholaus P. Brosowsky / N. P. Brosowsky**, with the original sample authors below.

- Repository: https://github.com/nbrosowsky/tonejs-instruments
- Fixed revision used by this app: `622c2f1c32c8cfce4158ddc3eb26e518ddef37e5`
- Upstream sample licensing statement: https://github.com/nbrosowsky/tonejs-instruments/blob/622c2f1c32c8cfce4158ddc3eb26e518ddef37e5/LICENSE.md
- Samples: **Creative Commons Attribution 3.0 Unported (CC BY 3.0)**: https://creativecommons.org/licenses/by/3.0/
- Original source listing: https://github.com/nbrosowsky/tonejs-instruments/blob/622c2f1c32c8cfce4158ddc3eb26e518ddef37e5/sample-source-info.txt
- Note/file map: https://github.com/nbrosowsky/tonejs-instruments/blob/622c2f1c32c8cfce4158ddc3eb26e518ddef37e5/Tonejs-Instruments.js

The upload ZIP contains the app's sample-player code and attribution, **not a full embedded sample library**. Required MP3 files are retrieved on demand from this fixed revision via jsDelivr, with raw.githubusercontent.com as a fallback. Only audio bytes are fetched; no remote JavaScript is evaluated. Browser storage may keep copies when permitted. First-time use needs internet access; caches may be unavailable or evicted.

## Original contributors (as credited by the collection)

| Banks | Original source credited upstream |
|---|---|
| Piano, bassoon, contrabass, flute, French horn, harp, organ, trombone, trumpet, tuba, violin, xylophone | Versilian Studios / VSO2 (VSCO Community) — http://vis.versilstudios.net/vsco-community.html |
| Electric bass, electric guitar, saxophone | Karoryfer — https://www.karoryfer.com/karoryfer-samples |
| Acoustic steel guitar | University of Iowa — http://theremin.music.uiowa.edu/ |
| Cello | Freesound, flcellogrl, `12408__flcellogrl__real-cello-notes` — https://freesound.org/people/flcellogrl/ |
| Nylon guitar | Freesound, quartertone, `11573__quartertone__classicalguitar-multisampled` — https://freesound.org/people/quartertone/ |
| Harmonium | Freesound, donyaquick, `330410__donyaquick__harmonium-samples-all-keys-and-drones` — https://freesound.org/people/donyaquick/ |
| Clarinet | Included in the pinned collection's instrument map; its original individual source is not separately named in `sample-source-info.txt`. Credit to the collection rather than inventing a specific original author. |

## Processing in this app

A curated subset of sampled pitches is used. Other pitches are obtained by playback-rate resampling. The app applies a bounded per-sample level adjustment, note velocity, a simple low-pass timbre adjustment and an attack/release envelope. Long sustained notes may use a private crossfaded loop copy. The source MP3 file is not changed. These are adaptations of the credited samples; no contributor endorsement is implied.

This is not a professional multi-velocity, pedal/resonance piano library. Natural range, articulation and timbral detail vary between instruments. The original 16 oscillator-based sounds remain available as explicit synthesis alternatives. The old bass/xylophone octave conventions are retained and labeled to avoid changing existing compositions silently.

## MIT license for upstream code / note-map material

MIT License

Copyright (c) 2018 Nicholaus P. Brosowsky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Verification boundary for this delivery

The pinned source maps and licensing statements were read through GitHub. The execution environment could not retrieve the actual remote audio bytes. Player decoding/scheduling, successful and failed download behavior, memory reuse and explicit synthesis mode were tested using synthesized audio responses at sample URLs. This is **not** an auditory evaluation of the actual sample recordings, nor a physical iPhone/Safari test. The application uses the real URLs above; the test responses are not present in production code.
