사용법
git 설치 및 다운로드

```
sudo apt install git
git clone https://github.com/shjeon0708/bigdata.git
```

실행 전 수업시간에 진행했던 배포파일은 모두 kubectl delete -f로 제거 후 진행하세요.


strimzi.io ClusterRoles 및 ClusterRoleBindings 배포
```
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
```

아파치 카프카 클러스터 생성
```
kubectl apply -f https://strimzi.io/examples/latest/kafka/kraft/kafka-single-node.yaml -n kafka
```

생성된 pod 확인
```
kubectl get all -n kafka
```
실습에 사용될 DB 배포 (MySQL 및 PostgreSQL)
```
kubectl apply -f bigdata/db/
```

Schema Registry, Kafka Connect 생성

```
kubectl apply -f bigdata/schema-registry.yaml
kubectl apply -f bigdata/kafka-connect.yaml
```

source 커넥터 및 sink 커넥터 생성
```
kubectl apply -f bigdata/kafka-mysql-source-connector.yaml
kubectl apply -f bigdata/kafka-postgres-sink-connector.yaml
```
MySQL의 test 데이터베이스에 있는 example 테이블이 PostgreSQL에서 읽어지는지 확인
```
kubectl get po -n kafka
kubectl exec -it {postgres pod} -n kafka -- psql -U postgres
```
PostgreSQL 접속 후 
```
\dt
select * from example;
```

옮겨진게 확인이 됐다면 

python pod 생성
```
kubectl apply -f bigdata/python.yaml
```

MySQL 접속 후 크롤링에 사용될 데이터베이스 및 사용자 생성
```
kubectl exec -it {mysql pod} -n kafka -- mysql -u root -p

CREATE DATABASE crawl_db DEFAULT CHARACTER SET utf8; #데이터베이스 생성
CREATE USER crawl_user IDENTIFIED BY 'Dankook1!'; #유저명 :crawl_user, 패스워드 Dankook1! 
GRANT ALL ON crawl_db.* TO crawl_user; crawl_db 데이터베이스의 권한을 crawl_user에게 주기

```

Python 접속 및 pip패키지 설치
```
kubectl exec -it python -n kafka -- /bin/bash

apt update && apt install vim #pod 접속 후 업데이트 및 vim 편집기 설치
pip install mysqlclient #pip을 이용해 mysqlclient 패키지 설치
pip install requests
pip install beautifulsoup4

```

크롤링 코드 작성
vim 편집기로 melon.py 생성
```
vi melon.py
```
```
import MySQLdb
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    RANK = 100  # 멜론 차트 순위가 1 ~ 100위까지 있음

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    req = requests.get('https://www.melon.com/chart/week/index.htm',
                       headers=header)  # 주간 차트를 크롤링 할 것임
    html = req.text
    parse = BeautifulSoup(html, 'html.parser')

    titles = parse.find_all("div", {"class": "ellipsis rank01"})
    singers = parse.find_all("div", {"class": "ellipsis rank02"})

    title = []
    singer = []

    for t in titles:
        title.append(t.find('a').text)

    for s in singers:
        singer.append(s.find('span', {"class": "checkEllipsis"}).text)
    items = [item for item in zip(title, singer)]

conn = MySQLdb.connect(
    user="crawl_user",
    passwd="Dankook1!",
    host="10.100.111.92", #host 확인하는 방법 kubectl get svc -n kafka 명령어로 mysql의 cluster-ip확인 CH13의 (20p 참조)
    db="crawl_db"
    # charset="utf-8"
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS melon")

cursor.execute("CREATE TABLE melon (`rank` int, title text, singer text)")


i = 1

for item in items:
    cursor.execute(
        "INSERT INTO melon (rank, title, singer) VALUES (%s, %s, %s)", (i, item[0], item[1]))
    i +=1

conn.commit()
```
코드 실행
```
python melon.py
```

source-connector와 sink-connetor 수정

kafka-mysql-source-connector.yaml

```
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: jdbc-mysql-source-connector
  namespace: kafka
  labels:
    strimzi.io/cluster: my-connect-cluster3
spec:
  class: io.confluent.connect.jdbc.JdbcSourceConnector
  tasksMax: 1
  config:
    mode: "bulk"
    poll.interval.ms: "86400000"
    #mode: "incrementing"
    #incrementing.column.name: "id"

    connection.url: "jdbc:mysql://mysql.kafka.svc.cluster.local:3306/crawl_db"
    connection.user: "crawl_user"
    connection.password: "Dankook1!"
    table.whitelist: "melon"
```

kafka-postgres-sink-connector.yaml

```
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: postgres-connector
  namespace: kafka
  labels:
    strimzi.io/cluster: my-connect-cluster3
spec:
  class: io.confluent.connect.jdbc.JdbcSinkConnector
  tasksMax: 1
  config:
    topics: "melon"
    connection.url: "jdbc:postgresql://postgres-service.kafka.svc.cluster.local:5432/postgres"
    connection.user: "postgres"
    connection.password: "root"
    auto.create: "true"
```

실행 시 PostgreSQL에 테이블이 없다면 source와 sink 커넥터를 삭제 후 다시 apply
```
kubectl delete -f bigdata/kafka-mysql-source-connector.yaml
kubectl delete -f bigdata/kafka-postgres-sink-connector.yaml

kubectl apply -f bigdata/kafka-mysql-source-connector.yaml
kubectl apply -f bigdata/kafka-postgres-sink-connector.yaml
```
