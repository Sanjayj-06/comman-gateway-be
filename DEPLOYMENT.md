# Deployment Guide

## Quick Deploy Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Prepare for deployment:**
   - Create a `render.yaml` file (see below)
   - Update requirements.txt to include PostgreSQL driver

2. **Deploy:**
   - Push code to GitHub
   - Go to https://render.com
   - Connect your GitHub repo
   - Render will auto-deploy using render.yaml

#### render.yaml
```yaml
services:
  - type: web
    name: command-gateway
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python start.py"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: command-gateway-db
          property: connectionString
      - key: PORT
        value: 10000

databases:
  - name: command-gateway-db
    databaseName: command_gateway
    user: command_gateway_user
```

### Option 2: Railway

1. **Install Railway CLI:**
```powershell
npm install -g @railway/cli
```

2. **Deploy:**
```powershell
railway login
railway init
railway up
```

3. **Add PostgreSQL:**
```powershell
railway add postgresql
```

### Option 3: Fly.io

1. **Install flyctl:**
```powershell
irm https://fly.io/install.ps1 | iex
```

2. **Deploy:**
```powershell
fly launch
fly deploy
```

## For PostgreSQL (Production)

### Update requirements.txt:
Add this line:
```
psycopg2-binary>=2.9.9
```

### Update .env:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

The code is already compatible - SQLAlchemy will automatically use PostgreSQL when DATABASE_URL points to a postgres:// URL!

## Environment Variables for Production

Make sure to set these in your hosting platform:

- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Usually 8000 or assigned by platform
- `PYTHON_VERSION` - 3.12 (in runtime.txt)

## Create runtime.txt (for some platforms):
```
python-3.12
```

## CORS Configuration

For production, update main.py CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # Your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Post-Deployment

1. **Seed the database:**
```powershell
# SSH into your deployment or use their CLI
python -m app.seed
```

2. **Get your admin API key** from the seed output

3. **Test the deployment:**
```powershell
curl https://your-app.render.com/health
```

## Free Tier Limitations

- **Render**: Spins down after inactivity, cold starts
- **Railway**: $5/month credit (usually enough)
- **Fly.io**: 3 VMs free, auto-sleep

Choose based on your needs!
