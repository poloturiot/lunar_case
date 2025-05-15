# Intro

In this challenge I built a service which consumes messages from a number of entities – i.e. a set of _rockets_ – and made the state of these available through a REST API.

# Get started

Here is how to quickly get this program running

## Setup a Python virtual environment

Create a new Python virtual environment

```bash
python3 -m venv lunar_case
```

Activate the virtual environment

```bash
source lunar_case/bin/activate
```

The virtual environment can be exited with:

```bash
deactivate
```

## Install the required libraries

```bash
pip install -r requirements.txt
```

## Run the API server and the test program

Run the API server:

```bash
python3 server.py
```

Run the test program :

Locate the executable that works for your system and run the following:

```bash
./rockets launch "http://localhost:8088/messages" --message-delay=500ms --concurrency-level=1
```

# Tests

Run all unit tests :

```bash
make test
```

Run all unit tests with test coverage :

```bash
make test_coverage
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

# Design choices

## Architecture Overview

The application follows a layered architecture:
1. **API Layer** (Flask Server) - Handles HTTP requests/responses
2. **Control Layer** (Control Center) - Manages rocket fleet and message processing
3. **Data Layer** (Rocket Model) - Represents individual rocket states

## Components

### API Layer (Flask)

- Built with [Flask](https://flask.palletsprojects.com/en/stable/) for its simplicity
- RESTful endpoints for messages, rockets, and missions
- JSON for data serialization/deserialization
- Thread-per-request model for concurrent processing

### Control Layer (Control Center)

The Control Center acts as the central orchestrator:
- Manages the fleet of rockets using a thread-safe dictionary
- Processes incoming messages
- Handles out-of-order message buffering
- Maintains consistency through locking mechanisms
- Provides query capabilities for rockets and missions

### Data Layer (Rocket Model)

Each rocket instance represents a unique spacecraft with:
- Immutable properties (ID, launch time, type)
- Mutable state (speed, mission, status)
- Thread-safe operations through individual locks
- Message buffering for out-of-order processing

Properties:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier given by the channel ID |
| `launch_time` | `str` | Time at which the first message for this rocket was sent |
| `last_update_time` | `str` | Time at which the last processed message for this rocket was sent |
| `last_message_number` | `int` | Number of the last processed message |
| `speed` | `int` | Current speed |
| `rocket_type` | `str` | Rocket type |
| `mission` | `str` | Mission the rocket is part of |
| `status` | `str` | Status can be `Launched` or `Exploded` |
| `explosion_reason` | `str \| None` | `null` if `status` is `Launched`, explains the reason of the explosion if `status` is `Exploded` |
| `message_buffer` | `list[tuple[int, dict]]` | Holds a list of messages that arrived out of order, and are waiting to be processed |
| `lock` | `threading.RLock` | Ensures only one thread is accessing the rocket's state, prevents race conditions |

## Features

### Thread locking

Each API request will create a new thread which is susceptible to modify the list of rockets and/or a rocket's parameters.

To prevent race conditions, thread locking is used. [RLock](https://docs.python.org/3/library/threading.html#rlock-objects) has been chosen since recursion is used when processing messages. That way, the same thread can re-acquire a lock it has already locked.

A lock is used for the fleet of rockets, and each rocket is individually locked to improve performance.

### Heap

Since messages can arrive out of order, they need to be stored in a buffer while waiting to be processed. 

A heap has been chosen to handle this. A heap queue is a priority queue. The smallest element is always at the root. Access, insertion and deletion are achieved using the priority queue algorithm. It's a great choice for efficiently managing messages that need to processed in a sorted order based on priority.

In Python, the [heapq](https://docs.python.org/3/library/heapq.html) module provides an implementation of the heap queue algorithm.

This facilitates operations, as the program doesn't need to sort messages or loop to find the next message to process.