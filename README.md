# 나스닥 100 볼린저 밴드 대시보드 실행 및 배포 가이드

이 문서에서는 VSCode(Visual Studio Code) 환경에서 Streamlit 기반의 나스닥 100 볼린저 밴드 웹 대시보드를 실행하는 방법과, Streamlit Community Cloud를 이용하여 무료로 호스팅(배포)하는 과정을 상세히 안내합니다.

---

## 0. 간단 실행방법
### 필수 라이브러리 설치
```bash
pip install streamlit yfinance plotly pandas
```

### 실행 방법:
1. 터미널에서 `python -m streamlit run app.py` 명령어로 앱 실행
2. 웹 브라우저에서 `https://bollinger.streamlit.app/` 접속

## 1. VSCode에서 로컬 실행하기 (내 PC에서 확인)

로컬 PC 환경에서 코드를 실행하고 테스트하는 과정입니다.

### 1.1 필수 프로그램 확인
- **Python**: 파이썬이 설치되어 있어야 합니다. (Python 3.8 이상 권장)
- **VSCode**: 코드 편집기

### 1.2 프로젝트 폴더 열기 및 파일 준비
1. VSCode를 실행합니다.
2. `파일(File)` > `폴더 열기(Open Folder)`를 클릭하여 작업할 폴더(예: `증권`)를 엽니다.
3. 해당 폴더 안에 `app.py` 파일이 존재하는지 확인합니다.

### 1.3 필수 라이브러리 설치
Streamlit과 데이터 분석, 차트 생성을 위한 라이브러리가 필요합니다.

1. VSCode 상단 메뉴에서 `터미널(Terminal)` > `새 터미널(New Terminal)`을 클릭합니다.
2. 터미널 창에 아래 명령어를 입력하고 `Enter` 키를 누릅니다.

```bash
pip install streamlit yfinance plotly pandas
```

### 1.4 애플리케이션 실행
설치가 완료되면 아래 명령어를 통해 앱을 실행합니다. 권한이나 경로 문제가 발생할 경우를 대비해 두 가지 방법을 제공합니다.

**방법 A (기본):**
```bash
streamlit run app.py
```

**방법 B (방법 A 실패 시 권장):**
```bash
python -m streamlit run app.py
```

명령어를 실행하면 로컬 서버가 시작되며, 터미널에 아래와 같은 메시지가 출력됩니다.
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
웹 브라우저가 자동으로 열리면서 대시보드가 표시됩니다. (자동으로 열리지 않으면 위 `Local URL` 주소를 브라우저 주소창에 복사하여 붙여넣으세요.)

### 1.5 앱 종료
터미널 창을 클릭한 후 `Ctrl + C`를 누르면 로컬 서버가 종료됩니다.

---

## 2. Streamlit Community Cloud를 이용한 무료 배포

로컬에서 확인한 대시보드를 인터넷상에 배포하여 스마트폰이나 외부 PC에서도 언제든 접속할 수 있게 만드는 과정입니다.

### 2.1 배포 전 준비사항: `requirements.txt` 생성
Streamlit Cloud가 어떤 라이브러리를 설치해야 하는지 알 수 있도록 명세서 파일을 만듭니다.

1. VSCode 좌측 탐색기에서 새 파일을 생성하고 이름을 `requirements.txt`로 지정합니다.
2. 파일 내용에 아래와 같이 패키지 이름을 한 줄씩 입력하고 저장(`Ctrl + S`)합니다.

```text
streamlit
yfinance
plotly
pandas
```

### 2.2 GitHub에 코드 업로드 (버전 관리)
코드를 클라우드에 배포하려면 먼저 GitHub 저장소에 코드가 있어야 합니다.

1. [GitHub](https://github.com/)에 접속하여 로그인합니다. (계정이 없다면 가입)
2. 우측 상단의 `+` 아이콘을 클릭하고 **New repository**를 선택합니다.
3. **Repository name**에 원하는 이름(예: `nasdaq-bollinger-dashboard`)을 입력합니다.
4. 공개 설정은 **Public**으로 유지하고, 하단의 **Create repository** 버튼을 클릭합니다.
5. 저장소가 생성되면, 화면 중앙의 **uploading an existing file** 링크를 클릭합니다.
6. VSCode 작업 폴더에 있는 `app.py`와 `requirements.txt` 파일을 드래그 앤 드롭으로 업로드합니다.
7. 화면 하단의 **Commit changes** 버튼을 눌러 파일을 저장소에 최종 반영합니다.

### 2.3 Streamlit Cloud 배포
이제 GitHub의 코드를 Streamlit 플랫폼과 연결하여 웹사이트를 생성합니다.

1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속합니다.
2. **Continue with GitHub** 버튼을 눌러 GitHub 계정으로 로그인/연동합니다.
3. 로그인 완료 후, 우측 상단의 **New app** 버튼을 클릭합니다.
4. **Deploy a public app from GitHub** 옵션을 선택합니다.
5. 배포 설정 항목을 아래와 같이 채웁니다.
   - **Repository**: 방금 생성한 GitHub 저장소 선택 (예: `본인아이디/nasdaq-bollinger-dashboard`)
   - **Branch**: `main` (또는 `master`)
   - **Main file path**: `app.py`
   - **App URL (선택)**: 원하는 커스텀 URL 뒷부분을 지정할 수 있습니다.
6. 우측 하단의 **Deploy!** 버튼을 클릭합니다.

### 2.4 배포 완료 및 접속
- 화면에 'Baking app...' 이라는 애니메이션이 표시되며 배포가 진행됩니다. (초기 배포 시 1~3분 정도 소요될 수 있습니다.)
- 배포가 완료되면 풍선 애니메이션과 함께 대시보드가 나타납니다.
- 브라우저 상단의 URL(예: `https://사용자지정주소.streamlit.app/`)을 복사하여 스마트폰 브라우저나 카카오톡 나에게 보내기에 저장해 두시면 언제든 접속 가능합니다.