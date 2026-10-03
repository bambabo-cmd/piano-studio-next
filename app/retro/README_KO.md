# 레트로 채널 엔진 — alpha.25

## 이번 수정
- 완성된 GME WebAssembly, JS 로더, 라이선스와 대응 소스를 함께 제공합니다.
- 앱의 실제 성공 배포(run 37095556195, artifact 11264765093)에서 회수한 엔진입니다.
- WebAssembly SHA-256: `7592b9dac0e4869ebc8eda165d9f4cb8814d44baf473441bf42347f7a070e4a6`
- 기존 JS 로더의 `import { createRequire } from 'module'`는 브라우저에서 해석할 수 없습니다.
  Node에서만 `node:module`을 동적 import하도록 변경했습니다. WASM 계산 코드는 변경하지 않았습니다.
- 빌더는 동봉 파일과 C++ 연결 코드의 고정 해시를 확인하고, 실제 WASM 채널 시험을 실행한 다음 사용합니다.
- 파일이 정상일 때 SDK/소스 다운로드나 재컴파일이 필요 없습니다. 파일 손상은 성공으로 숨기지 않습니다.
- 원래 소스 빌드 기능은 유지합니다. C++ 연결 코드를 수정하려면 재빌드와 새 체크섬이 필요합니다.

## 기능 경계
GME는 NSF/NSFE, GBS, HES, SPC, 제한된 SN76489/YM2612 VGM/VGZ의 채널 소리를 출력합니다.
음표 시퀀스를 읽는 도구가 아닙니다. 출력 채널을 기존 Basic Pitch로 채보하는 것은 별도의 선택입니다.
하드웨어 채널/채널 묶음과 실제 악기 한 종류는 같지 않습니다.
PSF/GSF/2SF는 현재 실행 엔진이 연결되지 않았습니다. 헤더 검사를 실행 지원으로 표시하지 않습니다.
SPC 공통 샘플과 VAB 악기는 별도의 게임 악기 창에서 작곡용으로 사용합니다.

## 검증
- Node에서 동봉한 실제 WASM으로 자체 제작 NSF/NSFE/GBS/HES/PSG·YM2612 VGM 및 제공된 FF5/FF6 실행.
- FF5/FF6 8개 채널 각각 8초씩 출력, 반복 출력 동일성 확인.
- Chromium Worker에서 같은 WASM으로 FF5 두 채널 15초씩 출력하여 실제 앱에 트랙 추가.
- 테스트 origin에서 module Worker가 제한되므로 Chromium 시험만 ESM 로더를 classic Worker용으로
  낮추고 로컬 바이트로 전달했습니다. WASM과 PCM 출력 로직은 실제 코드입니다. 네이티브 GME 대리 출력이 아닙니다.
- 실제 HTTPS origin에서의 최종 모듈 요청, iPhone/iPad Safari 및 모든 게임 호환성은 추가 검증 대상입니다.

## 출처와 수정 표시
Game Music Emu 고정 커밋: `dd3182a8bdae3ff761438632aace418fbcaed439`.
`gme-corresponding-source.zip`, `gme-license.txt`, `gme-readme.txt`를 배포에 함께 둡니다.
대응 소스에는 원래 라이브러리·연결 코드·빌드 방법과 alpha.25 로더 변경 설명이 들어 있습니다.
공개 저장소에 게임 음악 원본이나 사용자 곡을 넣지 마세요.
