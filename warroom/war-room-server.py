#!/usr/bin/env python3
"""Hermes AI Ventures - Trading War Room Live Server"""

import json
import redis
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
import threading
import time

app = Flask(__name__)

# Redis connection
r = redis.Redis(host='10.33.1.102', port=6379, decode_responses=True)

# Cognee connection
COGNEE_URL = "http://100.73.93.74:8000"

@app.route('/')
def index():
    return send_from_directory('.', 'war-room.html')

@app.route('/api/status')
def get_status():
    """Get live pipeline status"""
    try:
        # Redis connection test
        redis_ping = r.ping()
        redis_keys = r.dbsize()
        
        # Queue depths
        scout_queue = 0
        try:
            scout_queue = r.llen('queue:scout')
        except:
            pass
        
        analyst_queue = 0
        try:
            analyst_queue = r.llen('queue:analyst')
        except:
            pass
        
        strategist_queue = 0
        strategist_type = 'none'
        try:
            strategist_type = r.type('queue:strategist')
            if strategist_type == 'zset':
                strategist_queue = r.zcard('queue:strategist')
            elif strategist_type == 'list':
                strategist_queue = r.llen('queue:strategist')
        except:
            pass
        
        executor_queue = 0
        try:
            executor_queue = r.llen('queue:executor')
        except:
            pass
        
        done_queue = 0
        try:
            done_queue = r.llen('queue:done')
        except:
            pass
        
        # Agent status
        agent_status = {}
        try:
            agent_status = r.hgetall('agent:status')
        except:
            pass
        
        # Pipeline context
        pipeline_context = {}
        try:
            pipeline_context = r.hgetall('pipeline:shared_context')
        except:
            pass
        
        # Shared goals
        shared_goals = {}
        try:
            shared_goals = r.hgetall('shared:goals')
        except:
            pass
        
        # Shared memories
        shared_memories = {}
        try:
            shared_memories = r.hgetall('shared:memories')
        except:
            pass
        
        # Cognee health
        cognee_status = "unknown"
        try:
            import urllib.request
            with urllib.request.urlopen(f"{COGNEE_URL}/health", timeout=5) as response:
                cognee_data = json.loads(response.read().decode())
                cognee_status = cognee_data.get('health', 'unknown')
        except:
            cognee_status = "unreachable"
        
        # Get recent strategist signals (last 5)
        recent_signals = []
        try:
            if strategist_type == 'zset':
                items = r.zrange('queue:strategist', -5, -1, withscores=True)
                for item, score in items:
                    try:
                        signal = json.loads(item)
                        recent_signals.append({
                            'signal': signal.get('signal', 'N/A'),
                            'confidence': signal.get('confidence', 0),
                            'symbol': signal.get('symbol', 'N/A'),
                            'score': score
                        })
                    except:
                        pass
        except:
            pass
        
        # Get recent executor orders
        recent_orders = []
        try:
            orders = r.lrange('queue:executor', -5, -1)
            for order in orders:
                try:
                    order_data = json.loads(order)
                    recent_orders.append(order_data)
                except:
                    pass
        except:
            pass
        
        # Get done queue items
        recent_done = []
        try:
            done_items = r.lrange('queue:done', -5, -1)
            for item in done_items:
                try:
                    done_data = json.loads(item)
                    recent_done.append(done_data)
                except:
                    pass
        except:
            pass
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'redis': {
                'ping': redis_ping,
                'keys': redis_keys
            },
            'cognee': {
                'status': cognee_status
            },
            'queues': {
                'scout': scout_queue,
                'analyst': analyst_queue,
                'strategist': strategist_queue,
                'strategist_type': strategist_type,
                'executor': executor_queue,
                'done': done_queue
            },
            'agents': agent_status,
            'pipeline_context': pipeline_context,
            'shared_goals': shared_goals,
            'shared_memories': shared_memories,
            'recent_signals': recent_signals,
            'recent_orders': recent_orders,
            'recent_done': recent_done
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/agents')
def get_agents():
    """Get agent details"""
    agents = {
        'elon-scout': {
            'name': 'Elon-Scout',
            'role': 'Market Scanner',
            'status': 'active',
            'channel': 'luxe.marketing',
            'capabilities': ['Gap Detection', 'Regime Assessment', 'Price Monitoring']
        },
        'trump-analyst': {
            'name': 'Trump-Analyst',
            'role': 'Signal Analysis',
            'status': 'analyzing',
            'channel': 'luxe.content',
            'capabilities': ['Signal Analysis', 'Risk Scoring', 'Trade Setup Validation']
        },
        'osin-strategist': {
            'name': 'Osin-Strategist',
            'role': 'Trade Planning',
            'status': 'standby',
            'channel': 'queue:strategist',
            'capabilities': ['Entry/Exit Logic', 'Position Sizing', 'Order Construction']
        },
        'ken-executor': {
            'name': 'Ken-Executor',
            'role': 'Order Execution',
            'status': 'executing',
            'channel': 'queue:executor',
            'capabilities': ['Order Routing', 'Brokerage Execution', 'Fill Confirmation']
        }
    }
    
    return jsonify(agents)

@app.route('/api/trading')
def get_trading_status():
    """Get trading session status"""
    try:
        # Get trading session data from Redis
        trading_session = {}
        try:
            trading_session = r.hgetall('trading:session')
        except:
            pass
        
        # Get agent vision access config
        vision_access = {}
        try:
            vision_access = r.hgetall('agent:vision:access')
        except:
            pass
        
        return jsonify({
            'balance': trading_session.get('balance', '$993,546.55'),
            'positions': trading_session.get('positions', '0'),
            'vix': trading_session.get('vix', '18.5'),
            'regime': trading_session.get('regime', 'NORMAL'),
            'trades_today': trading_session.get('trades_today', '0'),
            'pnl_today': trading_session.get('pnl_today', '$0.00'),
            'vision_configured': bool(vision_access),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Hermes AI Ventures - Trading War Room Server")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api/status")
    print("🧠 Cognee: http://100.73.93.74:8000")
    print("🔴 Redis: 10.33.1.102:6379")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)