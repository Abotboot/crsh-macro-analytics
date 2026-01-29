# 📊 Crsh Macro Analytics Server

Beautiful real-time analytics dashboard for tracking Crsh Macro usage across all users.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd analytics_server
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

### 3. View Dashboard
Open your browser and go to:
```
http://localhost:8000
```

## 📈 What Gets Tracked

### User Statistics
- Total unique users
- Total cumulative hours across all users
- Active users (24h and 7d)
- Currently active sessions
- Average session duration

### Daily Metrics
- Daily active users (30-day chart)
- Daily usage hours (30-day chart)
- Session counts per day

### Top Users
- Username
- Total hours used
- Total sessions
- Last seen time

### Events (Optional)
- Macro recorded
- Macro played
- Macro created
- Hotkey assigned

## 🔧 Configuration

### Change Server Port
Edit `main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

### Deploy to Production

#### Option 1: Run on VPS/Cloud Server
1. Get a server (DigitalOcean, AWS, etc.)
2. Install Python 3.8+
3. Upload the `analytics_server` folder
4. Install dependencies: `pip install -r requirements.txt`
5. Run with production server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Use Heroku
```bash
# Install Heroku CLI, then:
heroku create crsh-macro-analytics
git push heroku main
```

#### Option 3: Use Railway/Render
- Connect your GitHub repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Update Client to Use Production Server
In `main.py` of the macro app:
```python
ANALYTICS_SERVER_URL = "https://your-server.com"  # Your production URL
```

## 🗄️ Database

Uses SQLite by default (`analytics.db`).

### Backup Database
```bash
cp analytics.db analytics_backup.db
```

### Use PostgreSQL (Production)
1. Install: `pip install psycopg2-binary`
2. Edit `database.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

## 📊 API Endpoints

### Get Overview Stats
```
GET /api/stats/overview
```

### Get Daily Stats
```
GET /api/stats/daily?days=30
```

### Get User Stats
```
GET /api/stats/users?limit=100
```

### Get Event Stats
```
GET /api/stats/events
```

## 🔒 Security

### Add Authentication
To protect your dashboard, add basic auth:

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic()

@app.get("/")
async def root(credentials: HTTPBasicCredentials = Depends(security)):
    # Check credentials
    if credentials.username != "admin" or credentials.password != "yourpassword":
        raise HTTPException(status_code=401)
    # ... rest of code
```

### HTTPS
Always use HTTPS in production. Most cloud providers (Railway, Render) provide free SSL.

## 🎨 Customize Dashboard

Edit `static/dashboard.html` to customize:
- Colors and theme
- Chart types
- Displayed metrics
- Refresh interval (default: 30 seconds)

## 📱 Mobile Responsive

The dashboard is fully responsive and works great on mobile devices!

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is available: `netstat -ano | findstr :8000`
- Try a different port

### Dashboard shows "Loading..." forever
- Check if server is running: `http://localhost:8000/health`
- Check browser console for errors
- Make sure CORS is enabled (it is by default)

### No data showing
- Make sure the macro app is running with `ENABLE_ANALYTICS = True`
- Check that `ANALYTICS_SERVER_URL` matches your server URL
- Check server logs for errors

## 📝 License

Part of Crsh Macro project. Free to use and modify.

---

**Made with ❤️ for the Crsh community**
