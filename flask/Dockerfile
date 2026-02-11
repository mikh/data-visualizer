FROM python:3.11-slim

WORKDIR /app
COPY *.py ./
COPY db ./db
COPY data ./data
COPY requirements.txt ./
COPY run-container.sh ./
COPY version ./

RUN mkdir -p untracked && mkdir -p untracked/data && mkdir -p untracked/logs

RUN pip install -r requirements.txt
RUN chmod +x run-container.sh

CMD ["./run-container.sh"]