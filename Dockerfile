FROM python:3.10.4

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx
RUN apt-get -y install vim

RUN mkdir /app 

# docker안에 srv/docker-server 폴더 생성
ADD . /app 
# 현재 디렉토리를 srv/docker-server 폴더에 복사

WORKDIR /app
# 작업디렉토리 설정

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

EXPOSE 8000 
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
