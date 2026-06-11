# Taiwan Stock AI Scanner

## Purpose

Build an AI-assisted stock and stock futures scanning system for the Taiwan market.

The system automatically scans the market and identifies potential trading opportunities.

## Target Users

Retail traders.

## Trading Style

Higher Timeframe:

* H1 Trend Analysis

Entry Timeframe:

* M5 Entry Confirmation

## Market

* Taiwan Stocks
* Taiwan Stock Futures

## Core Features

* Market Scanner
* Trend Detection
* Risk Management
* Signal Generation
* AI Scoring
* Backtesting
* Telegram Notification

## Trading Rules

Trend:

* EMA20 > EMA60 = Bullish
* EMA20 < EMA60 = Bearish

Entry:

* Pullback to EMA20

Risk:

* Fixed Risk Reward Ratio
* Default RR = 1:3

## Output Format

{
"symbol": "",
"direction": "",
"entry": 0,
"stop_loss": 0,
"target": 0,
"score": 0
}

## Future Roadmap

Phase 1

* Basic Scanner

Phase 2

* AI Scoring Engine

Phase 3

* Telegram Alerts

Phase 4

* Backtesting Engine

Phase 5

* Full Automation
