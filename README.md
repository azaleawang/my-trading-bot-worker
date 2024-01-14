# Trading-bot worker

## What's this for ?

### `server/main.py`

This application serves as a worker for executing Docker containers, which run automated trading scripts. It receives POST requests from the main web application (see [here](https://github.com/azaleawang/my-trading-bot/tree/main)).

```python
cd /home/ubuntu/bot-worker/server
uvicorn main:app --host 0.0.0.0 --port 3000
```

### `docker-monitor/main.py`

This program is designed to regularly monitor the status of Docker containers and send the gathered data to the main server.

```python
python3 /home/ubuntu/bot-worker/docker-monitor/worker.py
```
