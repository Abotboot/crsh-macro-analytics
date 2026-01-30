"""
Analytics API Server
Receives usage data from macro clients and serves dashboard
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import json

from database import init_db, get_db, User, Event, DailyStat
from database import Session as DBSession
from geo_utils import get_location_from_ip

app = FastAPI(title="Crsh Macro Analytics API")

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize database
init_db()

# Pydantic models for API
class SessionStart(BaseModel):
    user_id: str
    username: Optional[str] = None
    avatar_hash: Optional[str] = None
    discriminator: Optional[str] = None
    app_version: Optional[str] = None

class SessionEnd(BaseModel):
    session_id: str
    duration_minutes: float

class EventLog(BaseModel):
    user_id: str
    session_id: str
    event_type: str
    event_data: Optional[dict] = None

class Heartbeat(BaseModel):
    session_id: str

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r') as f:
            return f.read()
    return {"message": "Crsh Macro Analytics API", "status": "online"}

@app.post("/api/session/start")
async def start_session(session_data: SessionStart, request: Request, db: Session = Depends(get_db)):
    """Start a new session"""
    try:
        # Update or create user (no location tracking)
        user = db.query(User).filter(User.user_id == session_data.user_id).first()
        if not user:
            user = User(
                user_id=session_data.user_id,
                username=session_data.username,
                avatar_hash=session_data.avatar_hash,
                discriminator=session_data.discriminator,
                country=None,
                city=None,
                latitude=None,
                longitude=None,
                first_seen=datetime.utcnow(),
                total_sessions=0,
                total_hours=0.0,
                total_macros_created=0,
                total_macros_played=0,
                app_version=session_data.app_version
            )
            db.add(user)
        
        user.last_seen = datetime.utcnow()
        user.total_sessions += 1  # Increment every time exe is launched
        if session_data.username:
            user.username = session_data.username
        if session_data.avatar_hash:
            user.avatar_hash = session_data.avatar_hash
        if session_data.discriminator:
            user.discriminator = session_data.discriminator
        if session_data.app_version:
            user.app_version = session_data.app_version
        
        # Create new session
        session_id = str(uuid.uuid4())
        new_session = DBSession(
            user_id=session_data.user_id,
            session_id=session_id,
            start_time=datetime.utcnow(),
            app_version=session_data.app_version
        )
        db.add(new_session)
        
        db.commit()
        
        return {"session_id": session_id, "status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session/end")
async def end_session(session_data: SessionEnd, db: Session = Depends(get_db)):
    """End a session"""
    try:
        session = db.query(DBSession).filter(DBSession.session_id == session_data.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.end_time = datetime.utcnow()
        session.duration_minutes = session_data.duration_minutes
        
        # Update user total hours
        user = db.query(User).filter(User.user_id == session.user_id).first()
        if user:
            user.total_hours += session_data.duration_minutes / 60.0
            user.last_seen = datetime.utcnow()
        
        db.commit()
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session/heartbeat")
async def session_heartbeat(heartbeat: Heartbeat, db: Session = Depends(get_db)):
    """Keep session alive"""
    try:
        session = db.query(DBSession).filter(DBSession.session_id == heartbeat.session_id).first()
        if not session:
            return {"status": "session_not_found"}
        
        # Update user last seen
        user = db.query(User).filter(User.user_id == session.user_id).first()
        if user:
            user.last_seen = datetime.utcnow()
        
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.post("/api/event")
async def log_event(event: EventLog, db: Session = Depends(get_db)):
    """Log an event"""
    try:
        new_event = Event(
            user_id=event.user_id,
            session_id=event.session_id,
            event_type=event.event_type,
            event_data=json.dumps(event.event_data) if event.event_data else None,
            timestamp=datetime.utcnow()
        )
        db.add(new_event)
        
        # Update user macro stats
        user = db.query(User).filter(User.user_id == event.user_id).first()
        if user:
            if event.event_type == "macro_created" or event.event_type == "macro_recorded":
                user.total_macros_created += 1
            elif event.event_type == "macro_played":
                user.total_macros_played += 1
        
        db.commit()
        
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/overview")
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get overview statistics"""
    try:
        # Total unique users
        total_users = db.query(func.count(distinct(User.user_id))).scalar() or 0
        
        # Total hours (sum of all user hours)
        total_hours = db.query(func.sum(User.total_hours)).scalar() or 0.0
        
        # Total sessions
        total_sessions = db.query(func.count(DBSession.id)).scalar() or 0
        
        # Active users (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        active_users_24h = db.query(func.count(distinct(User.user_id))).filter(
            User.last_seen >= yesterday
        ).scalar() or 0
        
        # Active users (last 7 days)
        last_week = datetime.utcnow() - timedelta(days=7)
        active_users_7d = db.query(func.count(distinct(User.user_id))).filter(
            User.last_seen >= last_week
        ).scalar() or 0
        
        # Currently active sessions (no end time, started in last 15 minutes)
        # Consider sessions dead if no heartbeat for 15 minutes
        fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
        currently_active = db.query(func.count(DBSession.id)).filter(
            DBSession.end_time.is_(None),
            DBSession.start_time >= fifteen_min_ago
        ).scalar() or 0
        
        # Average session duration
        avg_duration = db.query(func.avg(DBSession.duration_minutes)).filter(
            DBSession.duration_minutes > 0
        ).scalar() or 0.0
        
        return {
            "total_users": total_users,
            "total_hours": round(total_hours, 2),
            "total_sessions": total_sessions,
            "active_users_24h": active_users_24h,
            "active_users_7d": active_users_7d,
            "currently_active": currently_active,
            "avg_session_minutes": round(avg_duration, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/daily")
async def get_daily_stats(days: int = 30, db: Session = Depends(get_db)):
    """Get daily statistics for the last N days"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily user activity
        daily_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            # Users active on this day
            users_count = db.query(func.count(distinct(User.user_id))).filter(
                User.last_seen >= date,
                User.last_seen < next_date
            ).scalar() or 0
            
            # Sessions on this day
            sessions_count = db.query(func.count(DBSession.id)).filter(
                DBSession.start_time >= date,
                DBSession.start_time < next_date
            ).scalar() or 0
            
            # Hours on this day
            hours = db.query(func.sum(DBSession.duration_minutes)).filter(
                DBSession.start_time >= date,
                DBSession.start_time < next_date
            ).scalar() or 0.0
            
            daily_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "users": users_count,
                "sessions": sessions_count,
                "hours": round(hours / 60.0, 2)
            })
        
        return daily_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/users")
async def get_user_stats(limit: int = 100, db: Session = Depends(get_db)):
    """Get user statistics"""
    try:
        users = db.query(User).order_by(User.total_hours.desc()).limit(limit).all()
        
        return [{
            "user_id": user.user_id,
            "username": user.username or "Anonymous",
            "avatar_hash": user.avatar_hash,
            "discriminator": user.discriminator,
            "country": user.country,
            "city": user.city,
            "total_hours": round(user.total_hours, 2),
            "total_sessions": user.total_sessions,
            "total_macros_created": user.total_macros_created,
            "total_macros_played": user.total_macros_played,
            "first_seen": user.first_seen.isoformat(),
            "last_seen": user.last_seen.isoformat(),
            "app_version": user.app_version or "Unknown"
        } for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/events")
async def get_event_stats(db: Session = Depends(get_db)):
    """Get event statistics"""
    try:
        # Get event counts by type
        event_counts = db.query(
            Event.event_type,
            func.count(Event.id).label('count')
        ).group_by(Event.event_type).all()
        
        return [{
            "event_type": event_type,
            "count": count
        } for event_type, count in event_counts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/popular-macros")
async def get_popular_macros(limit: int = 50, db: Session = Depends(get_db)):
    """Get most popular macros (most recorded and most played)"""
    try:
        # Get most recorded macros
        recorded_macros = db.query(
            Event.event_data,
            func.count(Event.id).label('count')
        ).filter(
            Event.event_type.in_(['macro_recorded', 'macro_created']),
            Event.event_data.isnot(None)
        ).group_by(Event.event_data).order_by(func.count(Event.id).desc()).limit(limit).all()
        
        # Get most played macros
        played_macros = db.query(
            Event.event_data,
            func.count(Event.id).label('count')
        ).filter(
            Event.event_type == 'macro_played',
            Event.event_data.isnot(None)
        ).group_by(Event.event_data).order_by(func.count(Event.id).desc()).limit(limit).all()
        
        # Parse macro data
        def parse_macro_data(macro_list):
            result = []
            for event_data_json, count in macro_list:
                try:
                    data = json.loads(event_data_json) if event_data_json else {}
                    macro_name = data.get('macro_name', 'Unknown')
                    actions = data.get('actions', [])
                    
                    # Extract action summary
                    action_summary = []
                    for action in actions[:10]:  # Show first 10 actions
                        action_type = action.get('type', 'unknown')
                        if action_type in ['KEY_PRESS', 'KEY_DOWN', 'KEY_UP']:
                            key = action.get('key', '?')
                            action_summary.append(f"Key: {key}")
                        elif 'MOUSE' in action_type:
                            button = action.get('button', 'left')
                            x = action.get('x')
                            y = action.get('y')
                            if x is not None and y is not None:
                                action_summary.append(f"Mouse {button} at ({x}, {y})")
                            else:
                                action_summary.append(f"Mouse {button}")
                        elif action_type == 'DELAY':
                            delay = action.get('delay', 0)
                            action_summary.append(f"Wait {delay}ms")
                    
                    result.append({
                        'macro_name': macro_name,
                        'count': count,
                        'total_actions': len(actions),
                        'action_summary': action_summary
                    })
                except:
                    pass
            return result
        
        return {
            'most_recorded': parse_macro_data(recorded_macros),
            'most_played': parse_macro_data(played_macros)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/geographic")
async def get_geographic_stats(db: Session = Depends(get_db)):
    """Get geographic distribution of users"""
    try:
        # Get country stats from users who have location data
        country_stats = db.query(
            User.country,
            func.count(User.id).label('count')
        ).filter(
            User.country.isnot(None),
            User.country != ''
        ).group_by(User.country).order_by(func.count(User.id).desc()).all()
        
        return {
            "countries": [{
                "country": country,
                "users": count
            } for country, count in country_stats],
            "total_with_location": sum(count for _, count in country_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/macros")
async def get_macro_stats(db: Session = Depends(get_db)):
    """Get macro statistics"""
    try:
        # Total macros created and played
        total_created = db.query(func.sum(User.total_macros_created)).scalar() or 0
        total_played = db.query(func.sum(User.total_macros_played)).scalar() or 0
        
        # Average macros per user
        user_count = db.query(func.count(User.id)).scalar() or 1
        avg_created = total_created / user_count
        avg_played = total_played / user_count
        
        # Top macro creators
        top_creators = db.query(User).filter(
            User.total_macros_created > 0
        ).order_by(User.total_macros_created.desc()).limit(10).all()
        
        # Most active macro users
        top_players = db.query(User).filter(
            User.total_macros_played > 0
        ).order_by(User.total_macros_played.desc()).limit(10).all()
        
        return {
            "total_macros_created": total_created,
            "total_macros_played": total_played,
            "average_macros_per_user": round(avg_created, 2),
            "average_plays_per_user": round(avg_played, 2),
            "top_creators": [{
                "username": user.username or "Anonymous",
                "macros_created": user.total_macros_created
            } for user in top_creators],
            "top_players": [{
                "username": user.username or "Anonymous",
                "macros_played": user.total_macros_played
            } for user in top_players]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/hourly")
async def get_hourly_stats(db: Session = Depends(get_db)):
    """Get hourly distribution of usage (what hours users are most active)"""
    try:
        # Get sessions from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        sessions = db.query(DBSession).filter(
            DBSession.start_time >= thirty_days_ago
        ).all()
        
        # Count sessions by hour of day
        hourly_counts = [0] * 24
        for session in sessions:
            hour = session.start_time.hour
            hourly_counts[hour] += 1
        
        return {
            "hourly_distribution": [
                {"hour": h, "sessions": hourly_counts[h]}
                for h in range(24)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
