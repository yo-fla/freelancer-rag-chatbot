# 프리랜서 고객 안내 챗봇

AWS 기반 RAG 챗봇 수업 프로젝트입니다. 2주차에는 기본 API 실행과 일정 데이터 조회를 확인합니다.

## 2주차 구현

- `GET /`: 실행 확인용 간단한 웹 화면
- `GET /health`: Lambda 실행 상태 확인
- `GET /availability`: DynamoDB에 저장한 가상 프리랜서 일정 조회
- S3: 소개서와 FAQ 샘플 문서 보관
- IAM: Lambda에 해당 일정 항목 조회와 로그 기록만 허용
- CloudWatch: API 접근 로그와 Lambda 실행 로그 수집, 보관 기간 7일

서울 리전(`ap-northeast-2`)을 사용합니다. API는 가상 정보만 보여 주는 공개 테스트용입니다. 로그인, 일정 수정 화면, 예약 확정, 문서 검색, AI 답변은 아직 구현하지 않았습니다.

## 개발 환경

Windows, VS Code, Codex, Git, Python을 사용합니다. AWS 환경 구성은 Codex의 AWS Core 연결 도구로 실행했습니다. AWS CLI는 이번 실행에 사용하지 않았습니다.

```powershell
python -m unittest discover -s tests -v
python scripts/package.py
```

Lambda 런타임은 Python 3.13입니다. boto3는 Lambda 런타임 제공 버전을 사용합니다. SDK를 로컬에서 사용하는 배포 스크립트에는 별도 boto3 설치와 기존 AWS 계정의 임시 인증이 필요합니다. 액세스 키나 토큰을 소스 코드에 넣지 않습니다.

## 데이터와 권한

일정 테이블은 `ownerId` 문자열을 기본 키로 사용합니다. 공개 API는 서버에서 정한 `demo` 항목만 `GetItem`으로 읽습니다. 클라이언트가 다른 사용자의 키를 지정할 수 없습니다. 최신 항목을 읽기 위해 `ConsistentRead=True`와 응답 `Cache-Control: no-store`를 사용합니다.

S3는 퍼블릭 접근 차단, ACL 비활성화, 저장 시 암호화, HTTPS 사용, 버전 관리를 적용합니다. 실제 고객 정보는 저장하지 않습니다. 사용량 기반 API 호출, DB 읽기·쓰기, 문서 저장과 로그에는 AWS 요금이 발생할 수 있습니다. 이번 단계에서는 Bedrock/OpenSearch 자원을 생성하지 않습니다.

## 이후 구현

S3 문서를 Bedrock Knowledge Bases로 동기화하고, 문서 검색 근거와 DynamoDB의 현재 일정을 함께 사용해 답변하는 흐름을 연결할 예정입니다. 문서 변경은 동기화 완료 후 검색에 반영됩니다.
