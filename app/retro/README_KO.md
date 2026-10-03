# 레트로 채널 엔진 — alpha.21

이 폴더는 배포 때 실제 Game Music Emu를 WebAssembly로 만드는 재현 소스입니다.
음원·ROM·BIOS는 포함하지 않습니다. 컴파일러·라이브러리만 첫 빌드 때 받습니다.

- GME 고정 커밋: dd3182a8bdae3ff761438632aace418fbcaed439
- Emscripten SDK: 3.1.64 (자체 설치, sudo 불필요)
- 같은 버전이 이미 이 앱의 공개 사이트에 배포돼 있으면 파일별 SHA-256과 소스 지문을
  검사해 이전 엔진을 재사용합니다. 재사용 때에도 실제 WASM 채널 검사를 재실행합니다.
- 실제 WASM을 Node에서 실행하고, 자체 제작 PSG VGM의 채널0은 유음·채널1은 무음인지
  통과해야 배포합니다. 오류 발생 시 이번 새 배포를 중단하며 기존 사이트를 지우지 않습니다.
- 도구는 기존 tools/build_site.py에서 호출합니다. .github/Pages 설정은 변경하지 않습니다.
- 브라우저에서는 필요할 때만 동일 출처의 모듈 Worker를 실행합니다. 작업 완료/닫기/중지
  시 Worker를 종료해 WASM 힙을 내려놓습니다. 128MiB WASM 힙, 출력 WAV 합계128MiB 제한.

## 라이선스 / 라이브러리 교체
Game Music Emu: Shay Green 및 기여자, LGPL 2.1 이상.
Nuked OPN2를 선택하여 GME의 MAME GPL 코어를 선택하지 않습니다.
배포 결과의 gme-license.txt/gme-readme.txt 및 gme-corresponding-source.zip에 원저자 표시,
원본 라이브러리 소스, 래퍼 소스와 빌드 명령을 제공합니다. 본 래퍼/worker는 원작 GME와
다른 수정 어댑터입니다. 라이브러리를 수정하여 같은 ABI로 다시 빌드하고 파일을 교체할 수 있습니다.
브라우저 앱과는 PCM/메타데이터 Worker 메시지로 연결되며, 원본 라이브러리를 폐쇄하지 않습니다.

```sh
python3 build_retro.py --output ./generated
```

게임 파일은 외부에 업로드하지 않습니다. 사용자 음악은 별도로 준비합니다.
NSF/NSFE/GBS/HES/SPC 및 GME가 처리하는 일부 VGM을 렌더링합니다.
VGM/VGZ는 이 어댑터에서 SN76489/YM2612만 허용하며 알 수 없는 칩/명령은 거부합니다.
채널 원음 렌더링은 게임 시퀀스의 음표 직접 추출이나 모든 악기의 이름 판별이 아닙니다.
일부 VGM 엔진은 PSG 여러 소리를 한 묶음으로 노출합니다. 노출된 채널/묶음 단위로 가져옵니다.
선택한 음정 채널에 기존 Basic Pitch AI를 적용하는 경로는 메인 UI에서 실행합니다.
FF6 연주 명령 직접 추출은 기존의 별도 메뉴이며 그대로 유지합니다.

VAB는 PS1 악기 뱅크 파서+ADPCM 샘플 듣기/저장입니다. 곡 시퀀스가 아닙니다.
PSF/GSF/2SF는 컨테이너/동반 파일 검사까지만 구현됐으며 실행은 아직 미지원입니다.

이 제작 환경에서는 SDK 외부 다운로드 제한으로 실제 WASM 컴파일을 실행하지 못했습니다.
네이티브 libgme 0.6.3 및 실제 UI/AI 경로를 검사했으며, 이를 WASM/Safari 검증이라 하지 않습니다.
실제 WASM 빌드와 검사는 사용자 저장소의 배포 로그에서 확인해야 합니다.
