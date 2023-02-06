# Server and client communication using WebSocket in Python

## Prerequisites

* Python >= 3.7
* websockets

## Setup and run

```
python -m venv websocket_app
. websocket_app/bin/activate
pip install -r requirements.py
```

Run application
```
python main.py
```

## Install client module as Python package
```
pip install entities/client
```
So then in any directory you can import Client class
```
from client import Client
```