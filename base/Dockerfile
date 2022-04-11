FROM debian:11 as python-build
ENV PYTHON_VERSION=3.9.12

RUN apt update
# pyenv deps
RUN apt install -y\
    make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
ENV HOME="/root"
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
WORKDIR ${HOME}
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
RUN pyenv install ${PYTHON_VERSION} -vvv
RUN pyenv global ${PYTHON_VERSION}

FROM debian:11 as run

ENV HADOOP_VERSION 3.2.3
ENV JAVA_VERSION 8.0.302-open

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
COPY --from=python-build /root /root

ENV JAVA_HOME=/root/.sdkman/candidates/java/current
ENV HOME="/root"
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV MULTIHOMED_NETWORK=1
ENV USER=root
ENV PATH $HADOOP_HOME/bin/:$PATH
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz

RUN curl -s "https://get.sdkman.io" | bash
RUN source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk install java ${JAVA_VERSION}
WORKDIR ${HOME}



RUN curl -O https://dist.apache.org/repos/dist/release/hadoop/common/KEYS
RUN gpg --import KEYS

RUN curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz
RUN curl -fSL "$HADOOP_URL.asc" -o /tmp/hadoop.tar.gz.asc
RUN gpg --verify /tmp/hadoop.tar.gz.asc
RUN tar -xvf /tmp/hadoop.tar.gz -C /opt/
RUN rm /tmp/hadoop.tar.gz*

RUN ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop
RUN mkdir /opt/hadoop-$HADOOP_VERSION/logs
RUN mkdir /hadoop-data

ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
