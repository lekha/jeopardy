FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    libffi-dev \
    libmysqlclient-dev \
    libopenblas-dev \
    libssl-dev \
    mysql-client \
    python3-dev \
    python3-pip

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.5 1

# UPDATE TO LATEST PIP
RUN pip3 install -U pip

# CREATE THE APPLICATION DIRECTORY
RUN mkdir -p /opt/jeopardy/src
RUN mkdir -p /opt/jeopardy/log
WORKDIR /opt/jeopardy/src

# INSTALL DEPENDENCIES
ADD ./requirements.txt .
RUN pip install -r requirements.txt

# INSTALL APPLICATION
ADD . .
RUN pip install -e .

CMD ["bash"]
