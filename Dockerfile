FROM python:3

MAINTAINER "https://github.com/bp-flugsimulator"

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY requirements_websockets.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_websockets.txt

COPY . .

CMD [ "python", "./setup.py", "test" ]
