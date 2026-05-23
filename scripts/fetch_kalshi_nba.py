#!/usr/bin/env python3
"""Fetch NBA playoff events from Kalshi API."""
import json
import urllib.request
import sys

def fetch_nba_events():
    url = "https://external-api.kalshi.com/trade-api/v2/events?limit=20&query=nba"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            for e in data.get('events', [])[:15]:
                ticker = e.get('event_ticker', '')
                title = e.get('title', '')
                status = e.get('status', '')
                close = e.get('close_time', '')
                print(f"{ticker:45s} | {title:60s} | {status:10s} | {close}")
    except Exception as ex:
        print(f"Error: {ex}", file=sys.stderr)

def fetch_nba_markets():
    url = "https://external-api.kalshi.com/trade-api/v2/markets?limit=20&query=nba"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            for m in data.get('markets', [])[:15]:
                ticker = m.get('market_ticker', '')
                title = m.get('title', '')
                price = m.get('last_price_dollars', '')
                volume = m.get('volume_dollars', '')
                status = m.get('status', '')
                print(f"{ticker:50s} | {title:50s} | {price:>8s} | {volume:>10s} | {status}")
    except Exception as ex:
        print(f"Error: {ex}", file=sys.stderr)

if __name__ == '__main__':
    print("=== NBA Events ===")
    fetch_nba_events()
    print("\n=== NBA Markets ===")
    fetch_nba_markets()
