FROM python:3.6-slim
WORKDIR /webapp
ADD . /webapp
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "application.py"]
