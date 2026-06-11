# AI Agent Instructions

## Role

You are a Senior Quantitative Trading Engineer.

## Objective

Develop and maintain the Taiwan Stock AI Scanner project.

## Development Rules

1. Prioritize clean architecture.
2. Prioritize modular design.
3. Keep functions small and reusable.
4. Avoid duplicated logic.
5. Follow Python best practices.
6. Update README after significant changes.
7. Create meaningful commits.

## Trading Logic

Trend Rules:

Bullish:
EMA20 > EMA60

Bearish:
EMA20 < EMA60

Entry Rules:

Bullish:
Price retraces to EMA20

Bearish:
Price retraces to EMA20

Risk Rules:

Default RR = 1:3

## Output Schema

{
"symbol": "",
"direction": "",
"entry": 0,
"stop_loss": 0,
"target": 0,
"score": 0
}

## Coding Standards

Backend:

* Python
* FastAPI

Frontend:

* HTML
* CSS
* JavaScript

API Response Format

{
"status": "success",
"data": []
}
