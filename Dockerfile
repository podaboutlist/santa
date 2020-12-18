FROM python:3

# git rev-parse --short HEAD
ARG COMMIT_SHA=""

WORKDIR /usr/src/santabot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GIT_COMMIT_SHA=${COMMIT_SHA}

ENTRYPOINT [ "python", "santabot.py" ]
