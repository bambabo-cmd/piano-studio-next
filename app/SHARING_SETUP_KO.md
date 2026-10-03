# 우리집 연주실 2 — 메일·Google Drive 공유 설정

## 추가 설정 없이 쓰는 방법
공유할 곡 JSON, 완성된 MP3/WAV 또는 곡 백업 ZIP을 준비한 다음 **파일 첨부 공유 · 메일/Drive 앱**을 누릅니다.
이 버튼은 기기에서 파일 공유를 지원할 때만 활성화됩니다. 공유창에 표시된 메일 앱 또는 Drive 앱을 선택하고,
그 앱에서 첨부와 전송/저장 대상을 확인합니다. 특정 앱을 강제로 열거나 수신 완료로 표시하지 않습니다.
앱을 설치해도 파일 종류·브라우저에 따라 공유 대상에 보이지 않을 수 있습니다.

PC의 웹메일만 쓸 때는 **파일 내려받기** 후 메일 작성창에 첨부합니다.
**첨부 포함 메일 파일 · EML**은 호환 메일 프로그램용 초안이며 자동 발송하지 않습니다.
EML은 파일 크기 20 MiB까지만 생성합니다. 큰 WAV/ZIP은 Drive 링크 공유가 적합합니다.

## Google Drive에 직접 올리기 — 앱 소유자가 처음 한 번 설정
직접 업로드 코드는 포함되어 있지만, 이 배포본에는 사용자 소유의 OAuth 클라이언트 ID가 없어 설정값이 비어 있습니다.
ChatGPT에 연결된 Google 계정/Drive 권한이 이 웹앱으로 전달되는 것은 아닙니다.
비밀번호·클라이언트 비밀키·접근 토큰을 저장소에 넣지 마세요.

1. Google Cloud Console에서 이 앱용 프로젝트를 만들거나 기존 프로젝트를 선택하고 **Google Drive API**를 사용 설정합니다.
2. Google Auth Platform에서 앱 이름·지원 이메일·대상 사용자를 설정합니다. 테스트 상태를 사용하는 경우 실제 로그인할 계정을 테스트 사용자로 추가합니다.
3. 데이터 액세스에는 다음 범위만 추가합니다.
   `https://www.googleapis.com/auth/drive.file`
   이 앱은 전체 Drive 열람 권한이나 Gmail 메일함 권한을 요청하지 않습니다.
4. OAuth 클라이언트를 **웹 애플리케이션**으로 만들고 **승인된 JavaScript 원본**에 아래 주소를 등록합니다.
   `https://bambabo-cmd.github.io`
   `/piano-studio-next/` 경로는 원본 항목에 넣지 않습니다. 이 앱은 팝업 토큰 방식이며 별도의 앱 서버용 비밀키를 쓰지 않습니다.
5. 발급된 `…apps.googleusercontent.com` 형식의 **클라이언트 ID**를 다음 파일에 넣고 업로드합니다.

```json
{
  "googleClientId": "발급받은_웹_클라이언트_ID.apps.googleusercontent.com"
}
```

파일 위치: `app/share-config.json`
이렇게 배포하면 각 기기에 같은 공개 클라이언트 ID를 반복 입력할 필요가 없습니다.
다른 방법으로 공유창의 **Google 연결 설정**에 ID를 입력해 이 기기에만 저장할 수도 있습니다.
사이트 전체 설정을 바꾼 뒤 이전의 기기별 ID가 남아 있다면 같은 화면에서 새 ID로 바꾸세요.

## 사용 순서
**공유할 파일 확인 → Google 로그인 준비 → Google 계정 연결 → 내 Drive에 비공개로 올리기 → 업로드 확인**

연결 버튼을 누르면 Google 창에서 계정과 권한을 직접 확인합니다.
로그인하거나 공유창을 열기만 해서는 곡을 업로드하지 않습니다.
업로드 버튼을 누른 뒤 파일 이름·크기를 다시 확인하면 내 Drive에 새 파일로 올립니다.
같은 이름의 기존 파일을 검색해서 덮어쓰지 않습니다. 반복 업로드하면 별도 파일이 생길 수 있습니다.
중지·네트워크 오류 이후에는 재시도 전에 Drive에 완성 파일이 있는지 확인하세요.

다른 사람이 읽게 하려면 받는 사람 이메일 한 개를 넣고 **받는 사람에게 읽기 권한 + 알림 메일…**을 누릅니다.
재확인 후 그 사람의 읽기 권한을 추가하고 Google 공유 알림 메일을 요청합니다.
이는 파일 첨부 메일이 아니라 **Drive 파일 링크 알림**입니다. 공개 링크 권한은 만들지 않습니다.
앱은 Google API 성공 응답을 확인하지만 수신자의 실제 메일 도착·열람을 확인하지 않습니다.
단순히 비공개 링크만 복사해 보내면 상대방에게 열기 권한이 없을 수 있습니다.

## 보안·연결 상태
접근 토큰은 현재 페이지 메모리에만 보관하고 곡·ZIP·localStorage에 넣지 않습니다.
페이지를 다시 열거나 토큰이 만료되면 다시 연결합니다. **연결 해제**는 권한을 해제하며 Drive 파일을 삭제하지 않습니다.
파일 업로드는 Google API에 직접 보내며 별도 중계 서버로 보내지 않습니다.
업로드한 파일을 앱 내부에서 다시 찾아 ZIP을 내려받는 Drive 파일 브라우저 기능은 이번 범위가 아닙니다.
Drive에서 ZIP을 내려받은 다음 곡 보관함의 **ZIP에서 복구**를 사용하세요.
Google 프로젝트 권한·테스트 사용자·소유 도메인·동의 화면 및 공개 배포 심사 요건은 Google 설정에 따라 확인해야 합니다.

## 이번에 실제 확인한 범위
실제 Google 프로젝트/OAuth 계정 연결/Drive 업로드/메일 전송은 실행하지 않았습니다.
로그인·업로드·권한 생성 UI는 명시적인 시험 응답으로 검사했습니다.
파일 생성·MIME 첨부·청크 분할·API 요청·승인/취소·오류 처리 코드는 실행 시험했습니다.

## 공식 문서
- 클라이언트 ID: https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid
- 브라우저 토큰 모델: https://developers.google.com/identity/oauth2/web/guides/use-token-model
- Drive 최소 범위: https://developers.google.com/workspace/drive/api/guides/api-specific-auth
- 파일 업로드: https://developers.google.com/workspace/drive/api/guides/manage-uploads
- 권한/알림: https://developers.google.com/workspace/drive/api/reference/rest/v3/permissions/create
- 기기 공유창: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share
