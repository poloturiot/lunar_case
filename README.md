# Setup
Create new virtual env
python3 -m venv lunar_case

Activate venv
source lunar_case/bin/activate

Stop venv
deactivate

Install flask library
pip install flask

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