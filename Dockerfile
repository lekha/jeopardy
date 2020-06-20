FROM python:3.8-slim AS jeopardy_web

RUN apt-get update && apt-get install -y \
    libffi-dev \
    libmariadb-dev \
    libopenblas-dev \
    libssl-dev

# CREATE THE APPLICATION DIRECTORY
WORKDIR /app
RUN mkdir /logs

# INSTALL DEPENDENCIES
ADD ./requirements.txt .
RUN pip install -r requirements.txt

# INSTALL APPLICATION
ADD . .
RUN pip install -e .

CMD ["bash"]
