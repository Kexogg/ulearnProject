FROM python:3.12-alpine AS base
EXPOSE 8000
WORKDIR /
COPY requirements.txt /
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /
RUN python3 manage.py collectstatic --no-input
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
