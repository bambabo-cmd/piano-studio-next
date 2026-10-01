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
