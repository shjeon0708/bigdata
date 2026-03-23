FROM ubuntu:20.04

# 1. 환경 변수 설정 
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
    HADOOP_VERSION=3.3.6 \
    HADOOP_HOME=/home/hadoop

ENV HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native" \
    PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin" \
    YARN_RESOURCEMANAGER_USER=root \
    YARN_NODEMANAGER_USER=root \
    HDFS_NAMENODE_USER=root \
    HDFS_DATANODE_USER=root \
    HDFS_SECONDARYNAMENODE_USER=root

# 2. 패키지 설치 및 하둡 설치 
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jdk wget net-tools vim ssh iputils-ping && \
    rm -rf /var/lib/apt/lists/* && \
    # 하둡 다운로드 및 압축 해제
    wget https://archive.apache.org/dist/hadoop/core/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -zxf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    rm hadoop-$HADOOP_VERSION.tar.gz && \
    mkdir -p $HADOOP_HOME/logs

# 3. 설정 파일 복사
COPY config $HADOOP_HOME/etc/hadoop/

# 4. 데이터 디렉토리 생성 및 네임노드 포맷
RUN mkdir -p /data/dfs/data /data/dfs/name /data/dfs/namesecondary && \
    $HADOOP_HOME/bin/hdfs namenode -format

VOLUME /data

# 5. 포트 설정
EXPOSE 9000 9870 9866 9867 9864 9868 8088

CMD ["hdfs"]
