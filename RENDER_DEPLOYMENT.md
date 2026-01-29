# 🚀 Deploy to Render (Free Hosting)

## Step 1: Prepare Your Code

1. The `analytics_server` folder is ready to deploy!
2. All necessary files are included:
   - `main.py` - API server
   - `database.py` - Database models
   - `requirements.txt` - Dependencies
   - `render.yaml` - Render configuration
   - `static/dashboard.html` - Web dashboard

## Step 2: Push to GitHub

Create a GitHub repository and push the `analytics_server` folder:

```bash
cd C:\Users\Abod\.gemini\antigravity\scratch\Macro\analytics_server

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Crsh Macro Analytics Server"

# Create a new repository on GitHub (https://github.com/new)
# Name it something like: crsh-macro-analytics

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/crsh-macro-analytics.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render

### Option A: Using Blueprint (Recommended)

1. Go to https://render.com and sign up (free)
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account
4. Select your `crsh-macro-analytics` repository
5. Click **"Apply"**
6. Render will automatically:
   - Read `render.yaml`
   - Install dependencies
   - Start the server
   - Give you a live URL!

### Option B: Manual Setup

1. Go to https://render.com and sign up
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `crsh-macro-analytics`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Click **"Create Web Service"**

## Step 4: Get Your Live URL

After deployment completes (2-3 minutes), you'll get a URL like:
```
https://crsh-macro-analytics.onrender.com
```

## Step 5: Update Your Macro App

Edit `main.py` in your macro app:

```python
# Change from localhost to your Render URL
ANALYTICS_SERVER_URL = "https://crsh-macro-analytics.onrender.com"
```

Then rebuild your exe:
```bash
cd C:\Users\Abod\.gemini\antigravity\scratch\Macro
python compile.py
```

## Step 6: Test Everything

1. Visit your dashboard: `https://crsh-macro-analytics.onrender.com`
2. Run your macro exe
3. Refresh dashboard - you should see the data!

---

## 🗄️ Database on Render

Render's free plan uses ephemeral storage, meaning:
- ✅ Database works great while server is running
- ⚠️ Database resets if server restarts (after inactivity)

### To Keep Data Permanent (Optional):

#### Option 1: Render PostgreSQL (Free)
1. In Render, click **"New"** → **"PostgreSQL"**
2. Create free database
3. Update `database.py`:
```python
# Install: pip install psycopg2-binary
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./analytics.db')
# Render automatically sets DATABASE_URL environment variable
```

#### Option 2: MongoDB Atlas (Free)
1. Create free cluster at https://www.mongodb.com/cloud/atlas
2. Get connection string
3. Update code to use MongoDB

---

## 🔧 Troubleshooting

### Server won't start
- Check Render logs for errors
- Verify all dependencies are in `requirements.txt`

### Database issues
- SQLite works fine for free tier
- Upgrade to PostgreSQL for production use

### Dashboard not loading
- Make sure `static` folder is in your repository
- Check that files uploaded correctly

---

## 💰 Free Tier Limits

Render free tier includes:
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ Automatic SSL/HTTPS
- ✅ Custom domains
- ⚠️ Service spins down after 15 min inactivity (first request takes ~30s)
- ⚠️ Ephemeral storage (use PostgreSQL for permanent data)

---

## 🎉 You're Live!

Share your dashboard URL with friends:
```
https://crsh-macro-analytics.onrender.com
```

Everyone who runs your macro exe will now be tracked automatically! 📊
