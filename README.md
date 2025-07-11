# Stock Analyzer

A simple gap-up stock analysis app running with Python and Docker.

---

## How to Build the Docker

docker build -t stock-analyzer .

---

## How to Run with Docker

docker run --env-file .env -p 5001:5000 stock-analyzer
