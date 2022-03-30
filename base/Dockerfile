FROM debian:11


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
    unzip

SHELL [ "/bin/bash", "-c" ]
RUN curl -s "https://get.sdkman.io" | bash
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java 8.0.302-open

ENV JAVA_HOME=/root/.sdkman/candidates/java/current

RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS
RUN gpg --import KEYS
ENV HADOOP_VERSION 3.2.3
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz

RUN curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz
RUN curl -fSL "$HADOOP_URL.asc" -o /tmp/hadoop.tar.gz.asc
RUN gpg --verify /tmp/hadoop.tar.gz.asc
RUN tar -xvf /tmp/hadoop.tar.gz -C /opt/
RUN rm /tmp/hadoop.tar.gz*

RUN ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop
RUN mkdir /opt/hadoop-$HADOOP_VERSION/logs
RUN mkdir /hadoop-data
ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV MULTIHOMED_NETWORK=1
ENV USER=root
ENV PATH $HADOOP_HOME/bin/:$PATH

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
