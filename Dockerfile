# Stage 1: Build React
FROM node:23-bullseye AS react-build
ARG REACT_VERSION=0.0.0
WORKDIR /app
COPY react/src ./src
COPY react/index.html ./
COPY react/package.json ./
COPY react/vite.config.js ./
COPY react/tailwind.config.js ./
COPY react/deps ./deps
COPY react/postcss.config.js ./
ENV VITE_URL_PREFIX=""
ENV VITE_REACT_VERSION=${REACT_VERSION}
RUN npm install && npm run build

# Stage 2: Flask + static files
FROM python:3.11-slim
WORKDIR /app
COPY flask/*.py ./
COPY flask/db ./db
COPY flask/data ./data
COPY flask/requirements.txt ./
COPY flask/run-container.sh ./
COPY flask/version ./
COPY --from=react-build /app/dist ./static
RUN mkdir -p untracked untracked/data untracked/logs
RUN pip install -r requirements.txt
RUN chmod +x run-container.sh
CMD ["./run-container.sh"]
