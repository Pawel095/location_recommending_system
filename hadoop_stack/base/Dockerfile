FROM python:3.9.12-bullseye as build-geomesa

RUN apt update && apt install zip unzip -y

# build geomesa, and bundle python package
SHELL [ "/bin/bash","-c" ]
RUN curl -s "https://get.sdkman.io" | bash ; source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java 8.0.302-open && sdk install mvnd
ENV JAVA_HOME=/root/.sdkman/candidates/java/current

ENV GEOMESA_VERSION=3.4.0

WORKDIR /geomesa-build
RUN git clone https://github.com/locationtech/geomesa.git
WORKDIR /geomesa-build/geomesa
RUN git checkout tags/geomesa-$GEOMESA_VERSION -b geomesa-$GEOMESA_VERSION && \
    source "$HOME/.sdkman/bin/sdkman-init.sh" &&  mvnd clean
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" &&  mvnd install -Ppython -DskipTests && \
    mkdir -p /packages/ && \
    cp geomesa-fs/geomesa-fs-dist/target/geomesa-fs_2.12-3.4.0-bin.tar.gz /packages/ && cp geomesa-spark/geomesa_pyspark/target/geomesa_pyspark-$GEOMESA_VERSION.tar.gz /packages/ && \
    tar -xvf /packages/geomesa-fs_2.12-3.4.0-bin.tar.gz -C /opt/

ENV GEOMESA_HOME=/opt/geomesa-fs_2.12-3.4.0
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" && mvnd dependency:copy-dependencies -pl geomesa-convert/geomesa-convert-osm/ \
    -DincludeScope=compile -DoutputDirectory=$GEOMESA_HOME/lib && \
    cp geomesa-convert/geomesa-convert-osm/target/geomesa-convert-osm_2.12-$GEOMESA_VERSION.jar $GEOMESA_HOME/lib && \
    rm -v $GEOMESA_HOME/lib/protobuf-java-2.5.0.jar && \
    curl https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/2.6.1/protobuf-java-2.6.1.jar -o $GEOMESA_HOME/lib/protobuf-java-2.6.1.jar

FROM python:3.9.13-bullseye

# hadoop and sdkman dependencies
RUN DEBIAN_FRONTEND=noninteractive \
    apt update && \
    apt install -y --no-install-recommends net-tools curl ca-certificates netcat gnupg curl zip unzip pv mc && \
    apt clean

SHELL [ "/bin/bash", "-c" ]
RUN curl -s "https://get.sdkman.io" | bash ; source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java 8.0.302-open
ENV JAVA_HOME=/root/.sdkman/candidates/java/current

SHELL [ "/bin/bash","-c" ]

RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS && gpg --import KEYS
ENV HADOOP_VERSION 3.2.3
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz

RUN curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz; \
    curl -fSL "$HADOOP_URL.asc" -o /tmp/hadoop.tar.gz.asc; \
    gpg --verify /tmp/hadoop.tar.gz.asc; \
    tar -xvf /tmp/hadoop.tar.gz -C /opt/; \
    rm /tmp/hadoop.tar.gz*

RUN ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop; \
    mkdir /opt/hadoop-$HADOOP_VERSION/logs; \
    mkdir /hadoop-data;

ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV MULTIHOMED_NETWORK=1
ENV USER=root
ENV GEOMESA_HOME=/opt/geomesa-fs_2.12-3.4.0
ENV PATH ${GEOMESA_HOME}/bin:$HADOOP_HOME/bin/:$PATH

# COPY --from=build-geomesa /geomesa-build/ /geomesa-build/
WORKDIR /packages/
COPY --from=build-geomesa /packages/ .
COPY executor-0.1.0-py3-none-any.whl .
COPY requirements.txt requirements.txt
COPY --from=build-geomesa /opt/ /opt/
RUN pip install -r requirements.txt

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
