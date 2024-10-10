
# CGV 영화 예매 모니터링 프로그램

이 애플리케이션은 CGV 영화 예매 가능 여부를 모니터링하고, 예약이 열리면 텔레그램 알림을 보내줍니다. 웹 스크래핑을 위해 Selenium을 사용하고, GUI 인터페이스는 Tkinter로 구현되어 있습니다. 또한, 영화의 제목과 개봉일 정보를 CGV 웹사이트에서 확인할 수 있는 기능을 포함하고 있습니다.

## 주요 기능

- **영화 정보 조회**: 영화 `midx` 값을 입력하여 영화의 제목과 개봉일을 확인할 수 있습니다.
- **예매 모니터링**: 특정 영화의 예매 페이지를 모니터링하고, 예약 버튼이 활성화되면 텔레그램으로 알림을 전송합니다.
- **텔레그램 알림**: 예약 버튼이 활성화되면 자동으로 텔레그램 채팅방으로 알림을 보냅니다.
- **GUI 인터페이스**: `midx` 값과 확인 간격을 입력하고 모니터링을 시작할 수 있는 간단한 Tkinter 기반 GUI 제공.

## 사전 준비 사항

다음 의존성들이 설치되어 있어야 합니다:

- Python 3.7+
- `tkinter` (대부분의 Python 배포판에 기본 설치되어 있습니다)
- `selenium` (`pip install selenium`)
- `webdriver_manager` (`pip install webdriver_manager`)
- `requests` (`pip install requests`)

## 사용 방법

1. **리포지토리 클론** 또는 스크립트를 다운로드합니다.
2. 필수 파이썬 패키지를 pip를 사용하여 설치합니다:
    ```bash
    pip install selenium webdriver_manager requests
    ```
3. **텔레그램 설정**:
    - 스크립트를 열어 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID` 값을 본인의 봇 토큰과 채팅 ID로 업데이트합니다.
    - 텔레그램 봇을 만들고 토큰을 얻으려면 [BotFather](https://core.telegram.org/bots#botfather)와 대화하세요.
4. 애플리케이션을 다음 명령어로 실행합니다:
    ```bash
    python app.py
    ```

## GUI 사용 방법

### 영화 정보 확인

1. `midx` 값을 입력합니다 (CGV 웹사이트의 영화 URL에서 확인할 수 있습니다).
2. "체크" 버튼을 눌러 영화 제목과 개봉일을 조회합니다.

### 모니터링 시작

1. `midx` 값과 확인 간격(분 단위)을 입력합니다.
2. "모니터링 시작" 버튼을 눌러, 설정한 간격마다 예약 버튼의 상태를 확인하고, 버튼이 활성화되면 텔레그램 메시지를 보냅니다.

### 텔레그램 테스트

- "텔레그램 테스트" 버튼을 눌러, 텔레그램 채팅방에 테스트 메시지를 전송할 수 있습니다.

## 예시

다음은 `midx` 값을 확인할 수 있는 CGV URL의 예시입니다:

```
http://www.cgv.co.kr/movies/detail-view/?midx=85813
```

위 URL에서 `midx`는 `85813`입니다.

## 주의 사항

- **헤드리스 모드**: 스크립트는 Chrome을 헤드리스 모드로 실행하므로, 실행 중에 브라우저 창이 열리지 않습니다.
- **스레딩**: 모니터링은 별도의 스레드에서 실행되어, GUI가 모니터링 중에도 응답 상태를 유지합니다.

## 문제 해결

- Selenium 또는 ChromeDriver 관련 오류가 발생하면 Chrome 브라우저가 최신 버전인지 확인하세요.
- 호환성 문제 발생 시 ChromeDriver를 다운로드하거나 업데이트해야 할 수 있습니다.
