# 12주차 AWS 구성

확인일: 2026-11-25 / 리전: 서울 `ap-northeast-2`

## 구성

| 서비스 | 설정 |
| --- | --- |
| API Gateway | HTTP API, Lambda 프록시 2.0, 기본 스테이지 자동 배포 |
| Lambda | `freelancer-chatbot-week2-api`, Python 3.13, 128MB, 제한 시간 10초 |
| DynamoDB | `freelancer-chatbot-week2-availability`, 기본 키 `ownerId`, PAY_PER_REQUEST |
| S3 | 소개서·FAQ와 배포 ZIP 보관, 비공개, AES256 암호화, HTTPS 사용, 버전 관리 |
| IAM | Lambda에 `demo` 일정 조회와 해당 함수의 로그 기록 권한 부여 |
| CloudWatch | Lambda 실행 로그와 API 접근 로그 수집, 7일 보관 |

Lambda 환경 변수는 `TABLE_NAME=freelancer-chatbot-week2-availability`, `OWNER_ID=demo`로 설정했다.
API 경로는 `GET /`, `GET /health`, `GET /availability`이며 요청 제한은 초당 2건, 순간 5건이다.

S3에 저장한 파일:

- `documents/profile.txt`
- `documents/faq.txt`
- `deployment/lambda.zip`

## 권한

`freelancer-chatbot-week2-lambda-role`은 해당 테이블의 `demo` 항목만 `GetItem`으로 읽는다.
로그 권한은 해당 함수 로그 그룹의 `CreateLogStream`, `PutLogEvents`로 제한했다.
API Gateway의 함수 실행 권한은 이번 API의 GET 경로와 같은 계정으로 제한했다.

## 실행 확인

[테스트 앱](https://4ihj2vcg89.execute-api.ap-northeast-2.amazonaws.com/)에서 두 API의 HTTP 200 응답과 CloudWatch 로그를 확인했다.
일정 조회 결과는 예약 종료일 `2026-12-04`, 다음 시작 가능일 `2026-12-07`이다.
로컬 테스트 5개도 통과했다.

현재 API는 가상 일정 조회용이며, 수정 기능은 제공하지 않는다.
AWS 자원은 과제 확인을 위해 유지 중이며 사용량에 따라 요금이 발생할 수 있다.
