FROM python:3.6.5
WORKDIR /app
ADD ./ ./
# WORKDIR /tmp/code
# ADD ./ ./
RUN pip install -r requirements.txt
CMD ["python", "scheduler.py"]
# EXPOSE 5432


# FROM dickeyxxx/heroku-cli:latest

