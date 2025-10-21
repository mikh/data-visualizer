FROM python:3.11-slim

WORKDIR /app
COPY *.py ./
COPY db ./db
COPY requirements.txt ./
COPY run-container.sh ./
COPY version ./

RUN pip install -r requirements.txt
RUN chmod +x run-container.sh

CMD ["./run-container.sh"]