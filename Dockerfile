FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_websockets.txt

COPY . .

CMD [ "python", "./setup.py", "test" ]
