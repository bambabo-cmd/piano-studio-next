# Game music import · alpha.20

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

## Independent test engine, not shipped in the app

The separate native reference test uses the environment's Game Music Emu (`libgme.so.0`)
to render eight actual SPC DSP channels independently. This is a playback/voice sanity test,
not proof that all note/control effects match a cycle-exact emulator. No libgme binary or
native helper is required by the web importer.
- https://github.com/libgme/game-music-emu
