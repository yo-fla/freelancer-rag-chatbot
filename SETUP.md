# 12주차 AWS 구성 기록

확인일: 2026-11-25 / 리전: 서울 `ap-northeast-2`

## 실행 주소

- 테스트 화면: https://4ihj2vcg89.execute-api.ap-northeast-2.amazonaws.com/
- 상태 확인: 위 주소의 `/health`
- 일정 조회: 위 주소의 `/availability`

## 구성 내용

1. S3 버킷에 `documents/profile.txt`, `documents/faq.txt`와 `deployment/lambda.zip`을 저장했습니다. 버킷은 계정별 고유 이름을 사용하며 비공개, ACL 비활성화, AES256 저장 암호화, HTTPS 강제, 버전 관리를 적용했습니다.
2. DynamoDB 테이블 `freelancer-chatbot-week2-availability`을 생성했습니다. 기본 키는 문자열 `ownerId`이며 `demo` 한 건만 사용합니다. 요금 모드는 PAY_PER_REQUEST, 저장 암호화는 기본 AWS 소유 키를 사용합니다. Streams, GSI, TTL, 복제는 사용하지 않습니다.
3. IAM 역할 `freelancer-chatbot-week2-lambda-role`은 Lambda 서비스만 맡을 수 있습니다. 해당 테이블의 `demo` 키를 `GetItem`으로 읽는 권한과 해당 함수 로그 그룹의 `CreateLogStream`, `PutLogEvents`만 허용했습니다.
4. Lambda 함수 `freelancer-chatbot-week2-api`에 ZIP을 배포했습니다. Python 3.13, 메모리 128MB, 제한 시간 10초입니다. 환경 변수는 `TABLE_NAME`과 `OWNER_ID=demo`입니다.
5. API Gateway HTTP API `freelancer-chatbot-week2`을 Lambda 프록시 형식 2.0으로 연결했습니다. `GET /`, `GET /health`, `GET /availability`만 허용하며 기본 스테이지를 자동 배포합니다. 제한은 초당 2건, 순간 요청 5건입니다. 이 제한은 최선 노력 방식으로 적용되며 비용 상한을 보장하지 않습니다.
6. API Gateway의 함수 실행 권한은 이번 API의 GET 경로와 같은 AWS 계정에 한정했습니다.
7. CloudWatch 로그 그룹 `/aws/lambda/freelancer-chatbot-week2-api`와 `/aws/apigateway/freelancer-chatbot-week2`을 만들고 보관 기간을 7일로 설정했습니다.

AWS 작업은 AWS Core의 계정 연결 도구로 실행했습니다. 설치형 AWS CLI와 장기 액세스 키는 사용하지 않았습니다.

## 확인 결과

- 로컬 단위 테스트 5개 통과: 상태 확인, 공개 항목 선별, 데이터 누락, DB 오류, 잘못된 경로와 메서드 처리.
- 배포된 화면에서 `/health` HTTP 200과 `status: ok` 확인.
- 배포된 화면에서 `/availability` HTTP 200, 예약 종료일 `2026-12-04`, 다음 시작 가능일 `2026-12-07` 확인.
- CloudWatch에서 두 요청의 상태 200과 Lambda 실행 기록 확인.

일정은 가상 데이터이며 예약을 확정하는 기능은 없습니다. 관리자 로그인과 일정 수정 API는 이후에 추가합니다. 현재 테이블을 수정할 때에는 콘솔 등 인증된 관리 경로를 사용해야 합니다.

## 운영과 정리

S3 저장, DynamoDB 읽기·쓰기, Lambda 실행, API 호출, 로그 저장 등에 사용량 요금이 생길 수 있습니다. Bedrock, OpenSearch, EC2, NAT Gateway는 이번 단계에서 생성하지 않았습니다. 리소스는 과제 확인을 위해 유지합니다. 실습 종료 후 데이터 보관 여부를 정한 다음 이번 프로젝트 자원만 정리합니다. 기존 계정의 다른 자원은 삭제하지 않습니다.

API를 실제 고객에게 제공하기 전에는 Cognito 등을 통한 관리자 인증, 권한 분리, 입력 검증과 운영용 보호 설정을 추가해야 합니다.
