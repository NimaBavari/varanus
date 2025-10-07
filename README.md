# Varanus

A lightweight monitoring daemon service. 

## Features

- Concurrent URL monitoring with configurable check intervals
- Response time and status code tracking
- Optional regex pattern matching on response content
- SQLite database storage
- Multi-threaded architecture with scheduler and worker threads

## Usage

Configure URLs and check intervals in `config.py`, then start the daemon:

```console
make start
```

Stop with `Ctrl+C`.

## Configuration

Edit `config.py` to define monitored resources:

```python
resources = [
    {"url": "https://example.com", "period": 30},
    {"url": "https://server.com", "period": 60, "pattern": r"^\d{3}-\d{2}-\d{4}$"}
]
```

- `url`: Target URL to monitor
- `period`: Check interval in seconds
- `pattern`: Optional regex pattern to search in response content

## Development

Install development dependencies:

```console
pip install -r dev_requirements.txt
```

Run code quality checks:

```console
make code-quality
```

## Database

Response data is stored in `monitoring.db` with timestamps, response times, status codes, and pattern matches.
