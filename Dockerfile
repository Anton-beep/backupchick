FROM python:3

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/src"

ENTRYPOINT  [ "python", "/usr/src/app/src/main.py" ]
