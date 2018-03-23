# 10th-amendment
2018년 제10차 개헌의 문재인 대통령 개헌안 비교 페이지입니다.

## 생성 및 확인 방법
```shell
$ pip install -r requirements.txt
$ python load_dbdata.py # initial db setup
$ python gen_data.py # generate vuejs data file
$ firefox docs/index.html
```

## DB 엔진 변경
기본적으로 `db.sqlite3` 이름으로 생성되는 sqlite db를 사용하고 있습니다.

편의를 위해 다른 DB 엔진을 사용하고 싶을 경우 `scripts/models.py` 파일의
`engine = create_engine('sqlite:///db.sqlite3')` 부분을 SQLAlchemy 표준 engine 표현식에 맞춰 변경해주세요.

## TODO
- [ ] 맨 위에 목차 추가하기
- [ ] 주요 개헌점에 하이라이트 표시하고 관련 뉴스 기사 연결하기
- [x] 맨 위에 개헌 진행상황 step 표시하기?
