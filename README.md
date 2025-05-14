# Setup

## Python virtual environment

Create new Python virtual environment

```bash
python3 -m venv lunar_case
```

Activate venv

```bash
source lunar_case/bin/activate
```

Stop venv

```bash
deactivate
```

## Libraries

Install all required libraries

```bash
pip install -r requirements.txt
```

# Run the API

Run the API server

```bash
python3 server.py
```

Running the test program

Locate the executable that works for your system and run the following:
```bash
./rockets launch "http://localhost:8088/messages" --message-delay=500ms --concurrency-level=1
```

# Tests

Run all unit tests

```bash
python -m unittest -v
```

# API Documentation

The server exposes the following endpoints:

## Messages
- **POST** `/messages`
  - Receives rocket telemetry messages
  - Requires JSON payload

## Rockets
- **GET** `/rockets`
  - Returns list of all rockets in fleet
  - Rockets sorted by launch time

- **GET** `/rockets/<rocket_id>`
  - Returns details for specific rocket
  - Returns 404 if rocket not found

## Missions
- **GET** `/missions`
  - Returns list of all unique missions
  - Missions sorted alphabetically

- **GET** `/missions/<mission>`
  - Returns all rockets for specific mission
  - Case insensitive mission name matching
  - Returns 404 if no rockets found for mission

## Error Responses
All endpoints may return:
- 400 Bad Request - Invalid JSON payload
- 500 Internal Server Error - Server-side error occurred

# Design choices

API redirect requests to control centers which oversees the fleet of rockets.

## Thread locking

To prevent race conditions, thread locking is used. [RLock](https://docs.python.org/3/library/threading.html#rlock-objects) has been chosen since recursion is used when processing messages. That way, the same thread can re-acquire a lock is has already locked.

## Heap

Since messages can arrive out of order, they need to be stored in a buffer while waiting to be processed. 

A heap has been chosen to handle this. A heap queue is a priority queue. The smallest element is always at the root. Access, insertion and deletion are achieved using the priority queue algorithm. It's a great choice for efficiently managing messages that need to processed in a sorted order based on priority.

In Python, the [heapq](https://docs.python.org/3/library/heapq.html) module provides an implementation of the heap queue algorithm.

This facilitates operations, as the program doesn't need to sort messages or loop to find the next message to process.