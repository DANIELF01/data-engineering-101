FROM python:3.9.1-alpine
RUN apk --no-cache add curl
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
COPY poetry.lock pyproject.toml /
RUN $HOME/.poetry/bin/poetry config virtualenvs.create false
RUN $HOME/.poetry/bin/poetry install
COPY web_server /app/web_server
WORKDIR /app/web_server
EXPOSE 5000
ENV FLASK_APP="main.py"
ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]




