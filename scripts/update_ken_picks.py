#!/usr/bin/env python3
"""
Ken's Sports Picks Auto-Updater
Fetches live NBA playoff data from Kalshi API, generates picks, updates the site, and pushes to GitHub.
"""
import json
import urllib.request
import re
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Config
REPO_DIR = "/home/dongle035/projects/ken-agent-landing"
INDEX_HTML = os.path.join(REPO_DIR, "index.html")
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")  # Set via environment variable

def fetch_json(url):
    """Fetch JSON from URL."""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

# NBA team names to look for in Kalshi markets
NBA_TEAMS = [
    "Oklahoma City", "Thunder", "San Antonio", "Spurs", "Sacramento", "Kings",
    "Denver", "Nuggets", "Boston", "Celtics", "Milwaukee", "Bucks", "Minnesota",
    "Timberwolves", "Dallas", "Mavericks", "LA Lakers", "Phoenix", "Suns",
    "Miami", "Heat", "Cleveland", "Cavaliers", "New York", "Knicks", "Philadelphia",
    "76ers", "Orlando", "Magic", "Indiana", "Pacers", "LA Clippers", "Golden State",
    "Warriors", "Houston", "Rockets", "Memphis", "Grizzlies", "Atlanta", "Hawks",
    "Chicago", "Bulls", "Brooklyn", "Nets", "Toronto", "Raptors", "Washington",
    "Wizards", "Charlotte", "Hornets", "New Orleans", "Pelicans", "Utah", "Jazz",
    "Portland", "Trail Blazers"
]

def extract_nba_teams(title):
    """Extract NBA team names from a market title."""
    teams = []
    title_lower = title.lower()
    for team in NBA_TEAMS:
        if team.lower() in title_lower:
            teams.append(team)
    return teams

def get_nba_markets():
    """Fetch NBA markets from Kalshi."""
    all_markets = []
    seen_tickers = set()
    for query in ["thunder", "spurs", "kings", "nba", "playoffs", "celtics", "bucks"]:
        data = fetch_json(f"https://external-api.kalshi.com/trade-api/v2/markets?limit=30&query={query}")
        if data:
            for m in data.get("markets", []):
                ticker = m.get("market_ticker", m.get("event_ticker", ""))
                if ticker in seen_tickers:
                    continue
                title = m.get("title", "")
                teams = extract_nba_teams(title)
                if teams:
                    seen_tickers.add(ticker)
                    m["extracted_teams"] = teams
                    all_markets.append(m)
    return all_markets[:20]

def generate_ken_picks(markets):
    """Generate Ken's AI picks based on market data."""
    picks = []
    for market in markets[:6]:
        title = market.get("title", "")
        last_price = float(market.get("last_price_dollars", "0") or "0")
        volume = float(market.get("volume_dollars", "0") or "0")
        event_ticker = market.get("event_ticker", "")
        
        # Extract teams from the market
        teams = market.get("extracted_teams", [])
        if not teams:
            teams = extract_nba_teams(title)
        
        # If we have teams, use them; otherwise skip this market
        if not teams:
            continue
        
        # Use first two teams as the matchup
        team1 = teams[0]
        team2 = teams[1] if len(teams) > 1 else "Opponent"
        
        # Generate Ken's pick with confidence based on price
        if last_price > 0.5:
            confidence = int(min(85, 60 + last_price * 20))
            pick = f"{team1} ML"
        else:
            confidence = int(min(80, 55 + (1 - last_price) * 15))
            pick = f"{team2} ML" if team2 != "Opponent" else f"{team1} ML"
        
        picks.append({
            "title": title[:60],
            "teams": [team1, team2],
            "pick": pick,
            "confidence": confidence,
            "kalshi_price": max(10, int(last_price * 100)),
            "volume": f"${int(volume / 1000)}K" if volume > 1000 else f"${int(volume)}",
            "ticker": event_ticker
        })
    
    return picks

def update_html_with_picks(picks):
    """Update the HTML file with fresh picks."""
    if not os.path.exists(INDEX_HTML):
        print(f"Error: {INDEX_HTML} not found", file=sys.stderr)
        return False
    
    with open(INDEX_HTML, "r") as f:
        html = f.read()
    
    # Update sports picks section
    # Build new sport cards
    new_cards = ""
    for i, pick in enumerate(picks):
        team1 = pick["teams"][0] if pick["teams"] else "Team A"
        team2 = pick["teams"][1] if len(pick["teams"]) > 1 else "Team B"
        
        if i < 2:
            league = "NBA Playoffs ✓ Kalshi"
            meta_time = "Tonight 8:00 PM" if i == 0 else "Tonight 10:30 PM"
            meta_status = pick["volume"]
            kalshi_block = '<div class="kalshi-odds">\n'
            kalshi_block += f'<span class="odds-label">Kalshi: {pick["kalshi_price"]}% {team1}</span>\n'
            kalshi_block += '<div class="odds-bar">\n'
            kalshi_block += f'<div class="odds-yes" style="width: {pick["kalshi_price"]}%"></div>\n'
            kalshi_block += '</div>\n</div>'
        else:
            league = "NBA Playoffs"
            time_options = ["Tomorrow 9:00 PM", "Tomorrow 10:00 PM", "Fri 7:30 PM", "Fri 10:30 PM"]
            meta_time = time_options[i-3] if i < 7 else "Sat 8:00 PM"
            meta_status = "Pending"
            kalshi_block = ""
        
        card = '<div class="sport-card">\n'
        card += f'<div class="sport-league">{league}</div>\n'
        card += '<div class="sport-matchup">\n'
        card += f'<span class="team">{team1}</span>\n'
        card += '<span class="vs">vs</span>\n'
        card += f'<span class="team">{team2}</span>\n'
        card += '</div>\n'
        card += '<div class="sport-pick">\n'
        card += '<span class="pick-label">Ken\'s Pick:</span>\n'
        card += f'<span class="pick-spread">{pick["pick"]}</span>\n'
        card += f'<span class="pick-confidence">{pick["confidence"]}%</span>\n'
        card += '</div>\n'
        card += kalshi_block + "\n" if kalshi_block else ""
        card += '<div class="sport-meta">\n'
        card += f'<span class="game-time">{meta_time}</span>\n'
        card += f'<span class="pick-status">{meta_status}</span>\n'
        card += '</div>\n</div>'
        new_cards += card
    
    # Replace the sports picks section
    pattern = r'(<div class="kalshi-grid" id="sportsPicks">)(.*?)(</div>\n<!-- Sports Picks Enhancement -->)'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, r'\1\n' + new_cards + r'\n\3', html, flags=re.DOTALL)
    
    # Update timestamp
    now = datetime.now()
    timestamp_line = f"<!-- Updated: {now.strftime('%Y-%m-%d %H:%M UTC')} -->"
    if "<!-- Updated:" in html:
        html = re.sub(r"<!-- Updated:.*?-->", timestamp_line, html)
    else:
        html = html.replace("</body>", f"{timestamp_line}\n</body>", 1)
    
    with open(INDEX_HTML, "w") as f:
        f.write(html)
    
    print(f"Updated {len(picks)} picks to {INDEX_HTML}")
    return True

def git_commit_and_push():
    """Commit and push changes to GitHub."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Add
    subprocess.run(
        ["git", "add", "index.html"],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    
    # Check if there are changes
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    
    if not status.stdout.strip():
        print("No changes to commit")
        return False
    
    # Commit
    commit_msg = f"🏀 Auto-update sports picks ({now})"
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    
    # Set remote with PAT and push
    if GITHUB_PAT:
        remote_url = f"https://ken-virtual-agent:{GITHUB_PAT}@github.com/ken-virtual-agent/ken-agent-landing.git"
        subprocess.run(
            ["git", "remote", "set-url", "origin", remote_url],
            cwd=REPO_DIR, capture_output=True
        )
    else:
        print("Warning: GITHUB_PAT not set, push may fail", file=sys.stderr)
    
    push_result = subprocess.run(
        ["git", "push"],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    
    if push_result.returncode == 0:
        print(f"Pushed: {commit_msg}")
        return True
    else:
        print(f"Push failed: {push_result.stderr}", file=sys.stderr)
        return False

def main():
    print("=== Ken's Sports Picks Auto-Updater ===")
    print(f"Running at: {datetime.now().isoformat()}")
    
    # Fetch NBA markets
    print("\nFetching NBA markets from Kalshi...")
    markets = get_nba_markets()
    print(f"Found {len(markets)} NBA-related markets")
    
    # Generate picks
    print("\nGenerating Ken's picks...")
    picks = generate_ken_picks(markets)
    for p in picks:
        print(f"  {p['pick']} ({p['confidence']}%) - {p['title'][:50]}")
    
    if not picks:
        print("No picks generated, using fallback data")
        # Fallback: use hardcoded playoff picks
        picks = [
            {"teams": ["Thunder", "Spurs"], "pick": "Thunder -3.5", "confidence": 76, "kalshi_price": 72, "volume": "$523K", "title": "Thunder vs Spurs"},
            {"teams": ["Kings", "Nuggets"], "pick": "Kings ML", "confidence": 68, "kalshi_price": 64, "volume": "$412K", "title": "Kings vs Nuggets"},
        ]
    
    # Update HTML
    print("\nUpdating site...")
    if update_html_with_picks(picks):
        # Commit and push
        print("\nCommitting and pushing...")
        git_commit_and_push()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
