Piano Studio Next / 우리집 연주실 2 / 2.0.0-alpha.3

1. 새 저장소 이름: piano-studio-next
2. 이 폴더의 "내용 전체"를 새 저장소 최상위에 올리세요.
   .github 폴더를 빼지 마세요. ZIP 자체를 올리거나 폴더 한 겹을 더 만들지 마세요.
3. Settings -> Pages -> Source -> GitHub Actions
4. Actions -> Build and deploy Piano Studio Next
   Pages 설정 전 실행이 실패했다면 Run workflow 또는 Re-run all jobs.
5. 성공 후 Pages에 표시되는 주소로 접속하세요.

기본 주소: https://bambabo-cmd.github.io/piano-studio-next/
화면 시안: https://bambabo-cmd.github.io/piano-studio-next/preview/
위 주소는 배포 성공 후 사용합니다. 이 파일을 만들 때 배포된 상태를 확인한 것은 아닙니다.

이 ZIP에는 새 소스/시안/빌드 도구가 있습니다.
원본 코드와 AI 자원은 GitHub Actions가 고정된 원본 커밋에서 가져와 실행본을 만듭니다.
PC에 별도 개발 도구 설치는 필요하지 않습니다. 원본 저장소는 변경하지 않습니다.
Actions Artifacts의 piano-studio-next-runtime에는 완성된 빌드 파일이 포함됩니다.

현재 실행본 구성은 원본 앱 + 메트로놈 바로가기/테마/별도 저장 공간/버전 전환 버튼입니다.
새 반응형 시안 전체와 엔진의 통합, 인식률·녹음 음량·양손 분리·편곡 개선은 아직 완료되지 않았습니다.
README.md에 정확한 범위와 검사 한계를 적었습니다.

먼저 버전 2를 배포한 다음, 별도 piano-studio-v1-switch-update의 내용물을 기존 piano-studio에 업로드하세요.
버전 1도 Settings -> Pages -> Source -> GitHub Actions로 선택하고 해당 v1 워크플로를 실행합니다.
두 버전은 같은 도메인이므로 각자의 캐시만 관리하도록 구성했습니다. 곡 목록은 자동 공유되지 않습니다.
