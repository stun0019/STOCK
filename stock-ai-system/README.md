# Taiwan Stock AI Scanner

## Overview

Taiwan Stock AI Scanner is a trading signal platform designed to identify stock and stock futures opportunities automatically.

## Features

* Trend Detection
* Signal Generation
* Risk Management
* AI Scoring
* FastAPI Backend
* Web Dashboard

## Tech Stack

Frontend

* HTML
* CSS
* JavaScript

Backend

* Python
* FastAPI

## Trading Strategy

Bullish Trend:
EMA20 > EMA60

Bearish Trend:
EMA20 < EMA60

Risk Reward:
1:3

## Project Structure

backend/
main.py
scanner.py
strategy.py
risk.py

frontend/
index.html
app.js
style.css

## Run Backend

pip install fastapi uvicorn

uvicorn main:app --reload

## API Endpoint

GET /signals

## Future Plans

* FinMind Integration
* Taiwan Futures Integration
* Telegram Alerts
* AI Scoring Engine
* Backtesting System
