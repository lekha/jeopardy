FROM python:3.8-slim AS jeopardy_backend

RUN apt-get update && apt-get install -y \
    libffi-dev \
    libmariadb-dev \
    libopenblas-dev \
    libssl-dev

# CREATE THE APPLICATION DIRECTORY
WORKDIR /app
RUN mkdir /database
RUN mkdir /logs

# INSTALL DEPENDENCIES
ADD ./backend/requirements.txt .
RUN pip install -r requirements.txt

# Replace default yoyo with a custom patched version
RUN rm /usr/local/bin/yoyo
RUN rm /usr/local/bin/yoyo-migrate
RUN ln -sf /database/patched_yoyo.py /usr/local/bin/yoyo

# ADD DATABASE MIGRATION FILES
ADD ./database /database

# INSTALL APPLICATION
ADD ./backend .
RUN pip install -e .

CMD ["bash"]
