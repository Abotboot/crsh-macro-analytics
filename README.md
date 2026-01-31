---
title: Crsh Macro Analytics
emoji: 🎮
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# Crsh Macro Analytics Server

Analytics dashboard and API for Crsh Macro application.

## Features
- User tracking and statistics
- Macro usage analytics
- Geographic distribution
- Real-time dashboard

## API Endpoints
- `GET /` - Dashboard
- `POST /api/session/start` - Start session
- `POST /api/session/end` - End session
- `POST /api/event` - Log event
- `GET /api/stats/overview` - Get overview stats
- `GET /api/stats/users` - Get user leaderboard
