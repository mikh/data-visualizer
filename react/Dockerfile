FROM node:23-bullseye

ARG URL_PREFIX=http://127.0.0.1:5000
ARG REACT_VERSION=0.0.0

WORKDIR /app

COPY src ./src
COPY index.html ./
COPY package.json ./
COPY vite.config.js ./
COPY tailwind.config.js ./
COPY run-container.sh ./
COPY deps ./deps
COPY postcss.config.js ./

ENV VITE_URL_PREFIX=${URL_PREFIX}
ENV REACT_VERSION=${REACT_VERSION}

RUN npm install
RUN npm install -g serve
RUN npm run build

EXPOSE 3000

RUN chmod +x run-container.sh

CMD ["/app/run-container.sh"]