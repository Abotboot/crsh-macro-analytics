# 🗄️ PostgreSQL Setup for Persistent Data

## Why PostgreSQL?
- ✅ **Free** on Render
- ✅ **Persistent** data (doesn't reset on redeploy)
- ✅ **Automatic** connection (Render handles it)
- ✅ **Scalable** for thousands of users

---

## Setup Steps (5 minutes):

### 1. Create PostgreSQL Database
1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Name: `crsh-macro-db`
4. Database: `analytics` (or any name)
5. User: (auto-generated)
6. Region: **Same as your web service** (important!)
7. Plan: **Free**
8. Click **"Create Database"**

### 2. Connect to Web Service
1. Wait 2 minutes for database to be ready
2. Go to your web service: `crsh-macro-analytics`
3. Click **"Environment"** tab
4. Render should auto-add `DATABASE_URL` environment variable
5. If not, manually add:
   - Key: `DATABASE_URL`
   - Value: Copy from PostgreSQL dashboard (Internal Database URL)

### 3. Deploy
1. The app will auto-detect PostgreSQL
2. Data will now persist forever! ✅

---

## What Happens:
- ✅ All user data saved to PostgreSQL
- ✅ Sessions, locations, macro stats persist
- ✅ Redeployments don't wipe data
- ✅ Database backups available

---

## Testing:
1. Add some test data via your exe
2. Redeploy the web service
3. Data should still be there! 🎉

---

## Backup (Optional):
From PostgreSQL dashboard:
- Click "Backups" tab
- Enable automatic backups
- Download backups anytime
