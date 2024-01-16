FROM python:3.12-alpine AS builder
EXPOSE 8000
WORKDIR /
COPY requirements.txt /
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /
RUN python3 manage.py collectstatic --no-input
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]

FROM builder as dev-envs
RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
EXPOSE 8000
CMD ["manage.py", "runserver", "0.0.0.0:8000"]