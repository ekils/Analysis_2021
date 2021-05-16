FROM python:3.6.5

WORKDIR /app
ADD ./ ./

# WORKDIR /tmp/code
# ADD ./ ./

RUN pip install -r requirements.txt
CMD ["python", "build_app.py"]
EXPOSE 5000
