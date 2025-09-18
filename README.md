Status of Last Deployment:<br>
<img src="https://github.com/bizoxe/exchange-rate-web-app/actions/workflows/ci.yaml/badge.svg?branch=master"><br>

# 💱 Exchange Rate Web Application

A practical assignment for the **Python Advanced** course.

---

## Task

- Develop an **asynchronous microservice** to get the exchange rate of a given currency against a fixed set of target currencies.
- Add support for specifying a **date** in the request.
- **Store cache on disk** to reduce unnecessary API calls.

---

## Description

### Libraries

- Use **`aiohttp server`** to create the asynchronous web application.
- Use **`aiohttp client`** for making asynchronous network requests.
- Use **`aiofiles`** to work with files asynchronously (read/write).

---

### API

You can use any public API to retrieve exchange rates.

A free option: [fawazahmed0/currency-api](https://github.com/fawazahmed0/currency-api)

- ✅ **List of available currencies:**  
  `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json`

- ✅ **Exchange rate for a given currency (latest):**  
  `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{currency}.json`  
  _Example_: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json`

- ✅ **Exchange rate for a given currency on a specific date:**  
  Replace `latest` with a date in `ISO-8601` format:  
  `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{currency}.json`  
  _Example_: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-09-28/v1/currencies/rub.json`

---

### Configuration

- Define a **static list of target currencies** to which the exchange rate should be returned.

---

### API Wrapper

Create a wrapper for handling API requests:

- Use **`aiohttp client`** for network communication.
- Implement a **high-level method** to fetch the exchange rate for a selected currency and date.
- Add a **method to read from cache (disk)**.
- If a cached value exists for the currency and date — return it without making network requests.
- On the first API call, build a response object from the fetched data and **save it to disk** in a pre-defined cache directory.

---

### Application Behavior

Develop a web application using `aiohttp server`:

- Implement a **single route handler** to retrieve exchange rate data.
- Support **queries both with and without a date**.
- If no date is provided, use **today’s date**.
- Use the API wrapper to get data:
  - If the data is cached — use the cached result.
  - If it’s a new request — fetch, format, and save to cache before responding.

---

### Error Handling

- If an **unknown currency** is provided — return **HTTP 404**.
- If an **invalid date** is provided — return **HTTP 422**.

---

### Type Hints

- Add **type annotations** throughout the codebase.
- Ensure the application passes `mypy` checks in **strict mode**.

---

## 📦 Dependencies used in my project

### Core Dependencies (`dependencies`)
- **[aiohttp](https://docs.aiohttp.org/)** – asynchronous HTTP server and client
- **[aiofiles](https://github.com/Tinche/aiofiles)** – async file I/O
- **[msgspec](https://jcristharif.com/msgspec/)** – fast data validation and serialization
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** – load environment variables from `.env` files
- **[redis](https://pypi.org/project/redis/)** – Redis client for Python

---

## 🛠 Developer Tools

### Group `dev`
- **[aioresponses](https://github.com/pnuckowski/aioresponses)** – mock HTTP responses for `aiohttp`
- **[coverage](https://coverage.readthedocs.io/)** – code coverage reports
- **[fakeredis](https://github.com/jamesls/fakeredis)** – in-memory fake Redis server for testing

### Group `lint`
- **[mypy](http://mypy-lang.org/)** – static type checker
- **[ruff](https://docs.astral.sh/ruff/)** – fast Python linter & formatter
- **[types-aiofiles](https://pypi.org/project/types-aiofiles/)** – type stubs for `aiofiles`

---

## 🧪 In addition to the assignment, I

- ✅ Wrote unit tests using Python's standard `unittest` module
- ✅ Added optional Redis-based caching alongside disk caching

---

## 🚀 Running the Application

### Clone repository:
```bash
git clone https://github.com/bizoxe/exchange-rate-web-app.git
```

### Start Valkey using Docker

```bash
docker compose up -d
```

### Run the Application

```bash
uv run webapp
```

### Once you launch the app, navigate:
- get exchange rates for a currency (latest):
http://localhost:8080/rates/usd
- get exchange rates for a currency on a specific date:
http://localhost:8080/rates/usd/2025-01-01

> **Note:**

You can use **file-based caching** instead of Redis. In this case, you don’t need to run Docker.

Use the following command to switch to file caching:

```bash
export STORAGE_TYPE=file
```
Then simply run the application with:

```bash
uv run webapp
```