# alpha.22 additions — composing with imported game samples

The app reads standard SPC snapshot/DSP sample-directory/BRR data without matching a game driver.
It stores BRR/VAG or generated PCM, loop boundaries, tuning provenance and approximate sampler envelopes.
This is not a full console DSP emulation, a universal sequence-to-MIDI converter, or a claim that
all game instruments have authoritative names and tuning information. Original uploaded files
are read locally; no commercial game samples are included in this public update ZIP.

The built-in NES/GB/PCE-style patches are generated waveform recreations, not vendor ROM dumps.
The existing VAB decoder and program layout use the documented PS1 structures from VGMTrans.
BRR arithmetic was checked against S-DSP documentation and Game Music Emu's published implementation.

Primary technical references:
- https://snes.nesdev.org/wiki/BRR_samples
- https://snes.nesdev.org/wiki/S-DSP_registers
- https://github.com/libgme/game-music-emu/blob/dd3182a8bdae3ff761438632aace418fbcaed439/gme/Spc_Dsp.cpp
- https://github.com/vgmtrans/vgmtrans/blob/master/src/main/formats/PS1/Vab.cpp
- https://developer.mozilla.org/en-US/docs/Web/API/AudioBuffer
- https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria

## Existing alpha.21 components and notices (retained)

# Game music import · alpha.21 (alpha.20 direct parser retained)

## Runtime scope

Piano Studio Next's JavaScript `PianoGameCore` is a bounded, adapted implementation of the
Final Fantasy VI AKAO-SNES v4 sequence format. It reads an uploaded SPC's in-memory sequence,
not recorded audio, and does not execute the SPC700 CPU. It is NOT the VGMTrans application,
a general SPC emulator, or a claim to support every game/format that VGMTrans supports.

This altered JavaScript port was made for Piano Studio Next. It uses the driver signatures,
command lengths, note durations, address relocation and event semantics documented in the
VGMTrans source. The VGMTrans Team is the source of that reverse-engineering work.

Primary sources:
- https://github.com/vgmtrans/vgmtrans
- https://github.com/vgmtrans/vgmtrans/blob/master/src/main/formats/AkaoSnes/AkaoSnesScanner.cpp
  reviewed Git blob: 2eb2002d001fd9c6ea2a7f8da3d646812a0f2f06
- https://github.com/vgmtrans/vgmtrans/blob/master/src/main/formats/AkaoSnes/AkaoSnesSeq.cpp
  reviewed Git blob: a7f1dffb389a00745d80022f4baeef2323408e56
- https://github.com/vgmtrans/vgmtrans/blob/master/LICENSE
  reviewed Git blob: eb9f3cd975a98fa477e59fd3462b108318c97764

Game files, ROMs, original game sound banks and commercial BIOS files are NOT supplied in the
public web upload. Users select their own local files; the importer sends none of these bytes
to a server. Any FF6 file/converted song included in a separate verification artifact is the
user-provided private test input, not part of the public application upload.

## Original VGMTrans notice (zlib)

Copyright (c) 2002-2025 The VGMTrans Team

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.

    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

    3. This notice may not be removed or altered from any source
    distribution.

## Historical alpha.20 independent test engine

The separate native reference test uses the environment's Game Music Emu (`libgme.so.0`)
to render eight actual SPC DSP channels independently. This is a playback/voice sanity test,
not proof that all note/control effects match a cycle-exact emulator. No libgme binary or
native helper is required by the web importer.
- https://github.com/libgme/game-music-emu


## alpha.21 — replaceable Game Music Emu worker backend

The additional importer renders chip output channels (sometimes a channel group), not
original sequence note events. It can optionally run the existing Basic Pitch on each
selected pitched channel. Original FF6 direct parsing above is unchanged.

- Library: Game Music Emu, Shay Green and contributors. LGPL 2.1 or later.
- Source: https://github.com/libgme/game-music-emu
- Pinned build commit: dd3182a8bdae3ff761438632aace418fbcaed439
- Compiler bootstrap: official Emscripten SDK 3.1.64, https://github.com/emscripten-core/emsdk
- The generated module, license text and corresponding source archive are served
  under app/retro. The C ABI wrapper, worker and build script are included for rebuilding.
- The frontend uses its own bounded file adapters and the Worker PCM protocol.
- The GME library uses its Nuked YM2612 option, not its MAME option.
- VGM importer supports SN76489/YM2612 commands; rejects unsupported chips,
  including YM2413 (the pinned GME VGM source has a disabled YM2413 wrapper).

## VAB bank reader

This new original JS bank reader was cross-checked against VGMTrans Vab.cpp
(Git blob 1193e190d90d88033e6560c19d584f30518f094b) and the PSX-SPX documentation.
It decodes PS1 ADPCM samples and displays region/sample references, not a song sequence.
- https://github.com/vgmtrans/vgmtrans/blob/master/src/main/formats/PS1/Vab.cpp
- https://psx-spx.consoledev.net/cdromfileformats/

PSF, GSF and 2SF emulators are not included in alpha.21; only container and
required companion-file checks are present. No copyrighted BIOS is supplied.

## alpha.25 changes
The positively identified AKAO-SNES direct note reader now includes FF5 v3 in addition
to FF6 v4. Driver signatures, v3 opcode semantics, durations and relocation follow the
VGMTrans AkaoSnesScanner.cpp and AkaoSnesSeq.cpp cited above. This is an altered JavaScript
implementation, not the VGMTrans application or a universal sequence decoder.

The GME binary and full corresponding source were recovered from Piano Studio Next's
successful own build 37095556195, artifact 11264765093 (commit 3bd7e37f25b50eafd95db738e7d0039e6dd48809).
The binary is unchanged. Its generated JavaScript loader has an explicitly marked correction:
Node built-ins are imported dynamically only under Node, not unconditionally in a browser Worker.
The bundle includes the modified readable loader, source archive, original library license,
checksums and repeatable actual-WASM tests. These app integration changes do not imply that
we wrote Game Music Emu, VGMTrans or their reverse-engineering work.
