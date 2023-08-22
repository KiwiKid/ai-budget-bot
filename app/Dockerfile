FROM python:latest
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "main.py"]
