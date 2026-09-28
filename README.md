# Piano Studio Next · 우리집 연주실 2

**버전: 2.0.0-alpha.3 — 새 저장소 시작용 초기 개발판**

Claude와 만든 `bambabo-cmd/piano-studio`를 버전 1로 보존하고, 이 저장소에서 버전 2를 이어 갑니다.

## 먼저 알아둘 현재 범위

이 저장소는 완성된 새 엔진을 뜻하지 않습니다. 다음 두 결과물을 구분합니다.

| 배포 경로 | 내용 |
|---|---|
| `/` | **실행용 초기 앱.** 원본 앱의 코드와 자원을 가져와 이름·저장 공간을 분리하고, 독립 메트로놈 바로가기와 시스템/다크/일반 테마를 추가합니다. 원래 녹음·채보·편집·편곡 기능은 원본 구현을 유지합니다. |
| `/preview/` | **새 반응형 UI 시안.** 아이폰·아이패드·노트북 배치, 예제 악보 편집, 실제 소리가 나는 메트로놈을 확인합니다. 실제 마이크·AI 채보·원본 프로젝트와는 아직 연결되지 않았습니다. |
| `/preview/devices.html` | 기기별 크기를 선택해서 위 시안을 확인하는 화면. |

**인식률, 녹음 음량, 양손/성부 분리, AI 첫 실행, 기타 코드·운지 편곡의 개선은 아직 완료되지 않았습니다.** 새 UI 시안 전체와 원본 엔진의 통합도 후속 작업입니다. 기존 기능을 보존했다는 말은 해당 기능의 정확도까지 개선·검증했다는 뜻이 아닙니다.

## 한글 계이름 붙여쓰기 (alpha.3)

실행용 앱의 **트랙 → ⌨ 타이핑으로 넣기**에서 `도도솔솔`과 `도 도 솔 솔`을 모두 지원합니다. `-`, `/`, 쉼, 반음, 옥타브, 왼손 표시와 넣을 위치는 기존 방식대로 사용합니다. `도미솔`은 세 음을 순서대로 넣습니다. 영어는 `c c g g`처럼 띄어 씁니다. `/preview/` 시안과는 별개입니다. 이번 변경·검사·한계는 `docs/TYPING_UPDATE_ALPHA3.md`를 확인하세요.

## GitHub에 업로드하고 실행하기

1. `piano-studio-next` 저장소를 만듭니다. GitHub Free에서 Pages를 쓸 경우 공개(Public) 저장소로 만듭니다.
2. ZIP을 풀고 **`UPLOAD_TO_piano-studio-next` 폴더 안의 파일·폴더 전체**를 저장소 최상위에 올립니다. 폴더 자체를 한 단계 더 중첩하지 않습니다. `.github` 폴더도 반드시 포함합니다. ZIP 파일만 올리는 것이 아닙니다.
3. 커밋한 후 **Settings → Pages → Build and deployment → Source → GitHub Actions**를 선택합니다. `Deploy from a branch`가 아닙니다.
4. **Actions → Build and deploy Piano Studio Next**에서 결과를 확인합니다. 최초 실행이 Pages 설정 전이라 실패했으면 설정 후 **Run workflow** 또는 **Re-run all jobs**를 누릅니다.
5. 배포가 성공하면 Pages 설정에 표시된 주소로 접속합니다.

계정과 저장소 이름이 위와 같을 때의 예상 주소:

```text
https://bambabo-cmd.github.io/piano-studio-next/
https://bambabo-cmd.github.io/piano-studio-next/preview/
```

이 패키지를 만들 때 이 주소의 실제 배포 완료를 확인한 것은 아닙니다.

### 왜 GitHub Actions를 쓰나요?

이 ZIP에는 **새 코드·설정·시안·검사 도구**가 들어 있습니다. 원본의 `index.html`, AI 번들, 악보 라이브러리, 아이콘은 Actions가 원본 공개 저장소에서 가져와 `dist/`에 함께 넣습니다. PC에 Python·Node·Git을 설치할 필요는 없습니다.

원본 기준은 움직이는 `main`이 아니라 다음 커밋으로 고정했습니다.

```text
bambabo-cmd/piano-studio
bd54de7e73274429c843aa0230623eaa1d700aa6
2026-09-27
```

빌드 과정은 원본 저장소를 읽기만 합니다. 원본 저장소에 푸시하거나 수정하지 않으며, 원본 커밋·파일 목록·수정 여부와 코드 보존을 검사합니다. 불일치가 있으면 배포용 빌드가 실패합니다. 외부 API 키나 유료 AI 서비스 키는 이 배포 과정에 필요하지 않습니다.

GitHub가 파일을 가져오는 것은 **빌드 시점**입니다. 배포된 앱이 열릴 때마다 원본 HTML을 다시 조립하는 방식은 아닙니다. 기존 앱이 사용하는 외부 모델/라이브러리 경로가 있다면 원래의 외부 통신은 그대로 남습니다.

빌드 성공 시 Actions의 **Artifacts → piano-studio-next-runtime**에도 전체 실행 파일이 생성됩니다. 이 결과물에는 원본에서 복사한 런타임 자원까지 포함됩니다. 이 저장소의 소스 ZIP과 구분하세요.

## 메트로놈 · 테마

상단에는 **버전 1 · 기존 / 버전 2 · Next** 전환 버튼을, 기본 화면 하단에는 **녹음 / 악보 보기 / 재생 / 메트로놈** 바로가기를 제공합니다. 메트로놈은 녹음과 곡 재생 없이 실행하며, 원래 앱의 메트로놈 설정과 동작을 사용합니다. 설정을 별도로 초기화하지 않습니다.

상단 **화면 모드**에서 **시스템 기본 / 다크 모드 / 일반 모드**를 선택합니다. 처음에는 다크 모드입니다. 새 테마를 적용할 때 원래 피아노롤의 색상 캐시도 갱신합니다. 악보 창 등은 원본 구현을 유지하므로 별도 UI 시안과 외형이 완전히 같지는 않습니다.

실행용 앱의 메트로놈은 원본 엔진, 시안의 메트로놈은 시안용 엔진입니다. 시안의 모든 옵션이 실행용 앱에 새로 이식됐다는 뜻이 아닙니다. iOS 잠금 화면·다른 앱으로 전환한 동안의 연속 재생은 보장하지 않습니다.

## 버전 1의 곡과 분리

버전 2는 별도 IndexedDB **`piano-studio-next-v2`**, 설정 키 **`psn-v2-`**를 사용합니다. 버전 1의 DB는 자동으로 가져오거나 삭제하지 않습니다.

기존 곡을 옮기려면 **버전 1 → 파일 → 곡 파일 저장(원음 포함)**으로 내보낸 뒤, 버전 2에서 **곡 파일 불러오기**를 사용합니다. 원본 프로젝트의 내보내기 형식 식별자는 바꾸지 않았습니다. 실제 중요한 곡의 왕복 호환은 별도 백업 후 확인해야 합니다.

## 버전 전환 버튼과 캐시

두 앱의 상단에서 현재 버전이 강조됩니다. 휴대폰에서는 `버전 1 / 버전 2`로 짧게 표시합니다. 현재 버전은 링크가 아니어서 실수로 다시 로드하지 않습니다.

- 버전 1: `https://bambabo-cmd.github.io/piano-studio/`
- 버전 2: `https://bambabo-cmd.github.io/piano-studio-next/`

일반 클릭은 현재 곡의 IndexedDB 저장 트랜잭션 완료를 기다린 뒤 같은 탭에서 이동합니다. 녹음·카운트인·분석/파일 처리 중이거나 저장에 실패하면 이동을 막고 안내합니다. Ctrl/Cmd+클릭 등 별도 탭 열기는 원래 브라우저 동작을 유지합니다. 이 경우 현재 탭을 떠나는 것이 아니며 두 버전의 재생 상태가 자동 동기화되는 것도 아닙니다. 주소창 입력/강제 종료까지 이 버튼이 보호하는 것은 아닙니다.

**버전 간 곡 자동 복사/동기화는 하지 않습니다.** 현재 버전의 곡만 저장하며 다른 버전의 DB를 열거나 수정하지 않습니다. 파일 내보내기/불러오기는 원본 구현을 사용합니다. 수동 양손 표기 등의 완전한 왕복 보존까지 이 배포본이 개선했다고 해석하지 마세요.

버전 2의 서비스 워커는 자기 경로의 구형 캐시만 정리합니다. 함께 제공한 `piano-studio-v1-switch-update`도 버전 1을 같은 방식으로 바꿉니다. **버전 1에 추가 묶음을 적용하지 않았거나 기존 서비스 워커가 아직 활성화 중이면, 버전 1의 옛 캐시 삭제 코드 영향이 남습니다.** 두 버전 배포 후 기존 탭/PWA를 닫고 다시 열어 새 워커를 적용하세요. 곡의 IndexedDB와 오프라인 파일 캐시는 서로 별개입니다. 다른 앱/예전 전역 `hps-*` 캐시는 함부로 삭제하지 않습니다.

## 검사 결과와 한계

alpha.3의 새 검사 기록은 `docs/TYPING_UPDATE_ALPHA3.md`입니다. `docs/TEST_REPORT.md` 및 기존 로그는 alpha.2의 과거 기록으로 보관했습니다. 빌드 입력은 합성 원본이며, 브라우저 검사는 원본 DOM을 흉내 낸 화면과 모의 저장 트랜잭션을 사용했습니다. 캐시 검사는 Node VM 모형입니다.

**실제 원본 전체를 이 작업 환경에서 내려받아 빌드·실행한 것은 아닙니다.** 외부 파일 다운로드와 브라우저의 HTTP 탐색이 환경 제한으로 차단되어, 실제 원본을 이용한 빌드·문법 검사는 업로드 후 Actions에서 실행하도록 넣었습니다. 사용자 계정의 Actions 배포 자체, 실제 IndexedDB/실기기 Safari, 실제 녹음·채보·악보 출력 품질 검증은 아직 하지 않았습니다. 모의 검사가 통과했다는 것을 실기기 검증으로 표현하지 않습니다.

## 개발 파일

```text
.github/workflows/pages.yml   원본 취득 → 검사 → 빌드 → Pages 배포
upstream.json                고정 원본 커밋/파일 목록
VERSION                      2.0.0-alpha.3
app/                         테마·메트로놈 바로가기·독립 캐시 코드
preview/                     새 UI 독립 시안
tools/build_site.py          원본 기능을 유지하는 별도 실행본 생성
tools/check_scripts.py       JavaScript 문법 검사
tests/                       합성 입력 기반 검사
docs/                        범위·검사 기록·기존 기능 보존 기준
```

로컬 개발 환경이 있는 경우:

```bash
git clone https://github.com/bambabo-cmd/piano-studio.git .upstream
git -C .upstream checkout bd54de7e73274429c843aa0230623eaa1d700aa6
python3 -m unittest discover -s tests -p 'test_*.py' -v
node tests/sw_contract.cjs
python3 tools/build_site.py --upstream .upstream --output dist
python3 tools/check_scripts.py dist
python3 -m http.server 8000 --directory dist
```

`dist/`가 이미 있으면 빌더는 덮어쓰지 않고 중단합니다. 필요한 결과물을 백업한 후 이전 `dist/`만 정리하고 다시 빌드하세요. 원본 `.upstream/`은 변경하지 않습니다.

## 공식 문서 · 원본

- 원본: https://github.com/bambabo-cmd/piano-studio
- 고정 커밋: https://github.com/bambabo-cmd/piano-studio/commit/bd54de7e73274429c843aa0230623eaa1d700aa6
- Pages 설정: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- 공식 정적 사이트 워크플로 참고: https://github.com/actions/starter-workflows/blob/main/pages/static.yml
