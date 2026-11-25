# 프리랜서 고객 안내 챗봇

프리랜서의 소개, FAQ, 의뢰 가능 일정을 안내하는 AWS 기반 챗봇 프로젝트.
12주차에는 테스트 API와 일정 조회 기능을 구현했다.

[테스트 앱](https://4ihj2vcg89.execute-api.ap-northeast-2.amazonaws.com/)

## API

| 경로 | 기능 |
| --- | --- |
| `GET /` | 실행 확인 화면 |
| `GET /health` | 서버 상태 확인 |
| `GET /availability` | DynamoDB의 가상 일정 조회 |

## 개발 환경

Python, VS Code, Codex를 사용했다. Lambda 런타임은 Python 3.13이다.

```powershell
python -m unittest discover -s tests -v
python scripts/package.py
```

테스트와 ZIP 생성은 Python 기본 라이브러리로 실행한다.
AWS 구성은 AWS Core로 진행했으며, 설정은 [SETUP.md](SETUP.md)에 정리했다.

현재 일정은 가상 데이터다. 문서 검색과 AI 답변 기능은 이후 구현한다.
