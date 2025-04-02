FROM ubuntu:20.04
#자바 환경변수 및 설치
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jdk && \
    rm -rf /var/lib/apt/lists/*

#하둡 환경변수 및 설치
ENV HADOOP_VERSION 3.3.6
ENV HADOOP_HOME /home/hadoop
ENV HADOOP_OPTS -Djava.library.path=$HADOOP_HOME/lib/native
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

ENV YARN_RESOURCEMANAGER_USER root
ENV YARN_NODEMANAGER_USER root

RUN apt-get update && \
    apt-get install -y wget net-tools vim && \
    wget http://archive.apache.org/dist/hadoop/core/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -zxf /hadoop-$HADOOP_VERSION.tar.gz && \
    rm /hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    mkdir -p $HADOOP_HOME/logs


COPY config  $HADOOP_HOME/etc/hadoop/

# 네임노드 Formatting 
RUN mkdir -p /data/dfs/data /data/dfs/name /data/dfs/namesecondary && \
    hdfs namenode -format
VOLUME /data


# 네임노드 및 데이터노드 간 통신을 위한 포트 설정 / Web UI 설정(네임노드 및 Yarn)
EXPOSE 9000 9870 9866 9867 9864 9868 8088

CMD ["hdfs"]
