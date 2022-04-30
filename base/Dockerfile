FROM python:3.9.12-bullseye as build-geomesa

RUN apt update && apt install zip unzip -y

# build geomesa, and bundle python package
SHELL [ "/bin/bash","-c" ]
RUN curl -s "https://get.sdkman.io" | bash
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java 8.0.302-open && sdk install mvnd
RUN pip install pyspark
ENV JAVA_HOME=/root/.sdkman/candidates/java/current

ENV GEOMESA_VERSION=3.4.0

WORKDIR /geomesa-build
RUN git clone https://github.com/locationtech/geomesa.git
WORKDIR /geomesa-build/geomesa
RUN git checkout tags/geomesa-$GEOMESA_VERSION -b geomesa-$GEOMESA_VERSION
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" &&  mvnd clean
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" &&  mvnd dependency:go-offline
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" &&  mvnd install -Ppython -DskipTests
RUN mkdir -p /packages/
RUN cp geomesa-spark/geomesa_pyspark/target/geomesa_pyspark-$GEOMESA_VERSION.tar.gz /packages/
RUN cp /geomesa-build/geomesa/geomesa-fs/geomesa-fs-spark-runtime/target/geomesa-fs-spark-runtime_2.12-${GEOMESA_VERSION}.jar /packages/
# RUN cp /geomesa-build/geomesa/geomesa-fs/geomesa-fs-spark/target/geomesa-fs-spark_2.12-${GEOMESA_VERSION}.jar /packages/

# FROM debian:11
FROM python:3.9.12-bullseye

# hadoop and sdkman dependencies
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    net-tools \
    curl \
    ca-certificates \
    netcat \
    gnupg \
    curl \
    zip \
    unzip \
    pv

SHELL [ "/bin/bash", "-c" ]
RUN curl -s "https://get.sdkman.io" | bash
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java 8.0.302-open && sdk install mvnd
ENV JAVA_HOME=/root/.sdkman/candidates/java/current

SHELL [ "/bin/bash","-c" ]

RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS
RUN gpg --import KEYS
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
ENV PATH $HADOOP_HOME/bin/:$PATH

# COPY --from=build-geomesa /geomesa-build/ /geomesa-build/
COPY --from=build-geomesa /packages/ /packages/
RUN pip install pyspark
RUN pip install /packages/geomesa_pyspark-3.4.0.tar.gz

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
