FROM python:3.10.4

ENV PYTHONVUFFERED 1

RUN apt-get -y update
RUN apt-get -y install vim

RUN mkdir /srv/docker-server 

# docker안에 srv/docker-server 폴더 생성
ADD . /srv/docker-server 
# 현재 디렉토리를 srv/docker-server 폴더에 복사

WORKDIR /srv/docker-server
# 작업디렉토리 설정

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

EXPOSE 8000 
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
