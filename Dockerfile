# Python 3.9가 설치된 상위 이미지에서 시작합니다.
FROM python:3.9

# 컨테이너 내부의 작업 디렉터리를 /app로 설정합니다.
WORKDIR /app


# requirements.txt 파일에 나열된 필요한 Python 라이브러리를 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app.py컨테이너가 이 이미지에서 시작될 때 Python을 사용하여 실행하도록 Docker에 지시합니다.
COPY app.py .

CMD [ "python", "app.py" ]
