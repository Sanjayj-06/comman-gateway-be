# Command Gateway - Quick Start Guide

## 🎯 What You Have Now

A fully functional Command Gateway backend with:
- ✅ FastAPI RESTful API
- ✅ SQLite database with SQLAlchemy ORM
- ✅ API key authentication
- ✅ Admin & Member roles
- ✅ Credit system for command execution
- ✅ Rule-based command filtering (regex patterns)
- ✅ Transaction-safe command execution
- ✅ Comprehensive audit logging
- ✅ Seed data with default admin & rules

## 🚀 Getting Started

### 1. Your Admin Credentials

```
Username: admin
API Key: HnXVX7endKivrmVLnigm6i7RAPwBIGY85yDVSAd96Nec9XsPYIYavqIlC1tORf2I
Credits: 1000
```

**⚠️ SAVE THIS API KEY - You'll need it for all admin operations!**

### 2. Start the Server

```powershell
python start.py
```

The API will be available at: `http://localhost:8000`

- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 3. Test the API

#### Using PowerShell:

```powershell
# Health check
curl http://localhost:8000/health

# Get admin info
$headers = @{"X-API-Key"="HnXVX7endKivrmVLnigm6i7RAPwBIGY85yDVSAd96Nec9XsPYIYavqIlC1tORf2I"}
curl -Headers $headers http://localhost:8000/users/me

# Submit a safe command
$body = @{command_text="ls -la"} | ConvertTo-Json
curl -Method POST -Headers $headers -Body $body -ContentType "application/json" http://localhost:8000/commands/

# Submit a dangerous command (will be rejected)
$body = @{command_text="rm -rf /"} | ConvertTo-Json
curl -Method POST -Headers $headers -Body $body -ContentType "application/json" http://localhost:8000/commands/
```

#### Using Python test script:

```powershell
# Install requests if needed
pip install requests

# Run comprehensive tests
python test_api.py
```

## 📋 Key API Endpoints

### User Management
- `POST /users/` - Create user (admin only) - returns API key once
- `GET /users/me` - Get current user info
- `GET /users/me/stats` - Get user statistics
- `GET /users/me/commands` - Get command history
- `GET /users/` - List all users (admin only)
- `PATCH /users/{user_id}/credits` - Update credits (admin only)

### Rule Management
- `POST /rules/` - Create rule (admin only)
- `GET /rules/` - List all rules
- `PUT /rules/{rule_id}` - Update rule (admin only)
- `DELETE /rules/{rule_id}` - Delete rule (admin only)

### Command Execution
- `POST /commands/` - Submit command
- `GET /commands/` - Get command history
- `GET /commands/{command_id}` - Get specific command

### Audit Logs
- `GET /audit/` - Get audit logs (admin only)
- `GET /audit/user/{user_id}` - Get user's audit logs (admin only)

## 🎮 Example Workflows

### 1. Create a New User

```powershell
$headers = @{
    "X-API-Key"="HnXVX7endKivrmVLnigm6i7RAPwBIGY85yDVSAd96Nec9XsPYIYavqIlC1tORf2I"
    "Content-Type"="application/json"
}
$body = @{
    username="john_doe"
    role="member"
} | ConvertTo-Json

curl -Method POST -Headers $headers -Body $body http://localhost:8000/users/
```

**Response includes the new user's API key - save it immediately!**

### 2. Submit Commands

```powershell
# Safe command (will execute)
$userHeaders = @{
    "X-API-Key"="USER_API_KEY_HERE"
    "Content-Type"="application/json"
}
$body = @{command_text="git status"} | ConvertTo-Json
curl -Method POST -Headers $userHeaders -Body $body http://localhost:8000/commands/

# Dangerous command (will be rejected)
$body = @{command_text="rm -rf /"} | ConvertTo-Json
curl -Method POST -Headers $userHeaders -Body $body http://localhost:8000/commands/
```

### 3. Create a New Rule

```powershell
$adminHeaders = @{
    "X-API-Key"="HnXVX7endKivrmVLnigm6i7RAPwBIGY85yDVSAd96Nec9XsPYIYavqIlC1tORf2I"
    "Content-Type"="application/json"
}
$body = @{
    pattern="^docker\\s+"
    action="AUTO_REJECT"
    description="Docker commands not allowed"
    priority=0
} | ConvertTo-Json

curl -Method POST -Headers $adminHeaders -Body $body http://localhost:8000/rules/
```

## 📊 Pre-configured Rules

| Pattern | Action | Description |
|---------|--------|-------------|
| `:(){ :\|:& };:` | AUTO_REJECT | Fork bomb |
| `rm\s+-rf\s+/` | AUTO_REJECT | Delete root directory |
| `mkfs\.` | AUTO_REJECT | Format filesystem |
| `git\s+(status\|log\|diff\|branch\|show)` | AUTO_ACCEPT | Safe git commands |
| `^(ls\|cat\|pwd\|echo\|which\|whoami)` | AUTO_ACCEPT | Safe basic commands |

## 🎬 Next Steps for Hackathon

### Required for Submission:

1. **Create Frontend** - Build a CLI or web interface
2. **Demo Video** - Record 2-3 minute walkthrough
3. **README** - Already created! Update with your demo details
4. **GitHub Repo** - Push all code

### Bonus Features (Optional):

1. **Deploy** - Use Render, Railway, or Fly.io
2. **REQUIRE_APPROVAL** - Add approval workflow
3. **Notifications** - Telegram/Email for approvals
4. **Rule Conflicts** - Detect overlapping patterns

## 🔧 Project Structure

```
comman-gateway-be/
├── main.py              # FastAPI app
├── start.py             # Server launcher
├── test_api.py          # API test script
├── requirements.txt     # Dependencies
├── .env                 # Configuration
├── README.md            # Full documentation
└── app/
    ├── dependencies.py  # Auth middleware
    ├── schemas.py       # Pydantic models
    ├── utils.py         # Helper functions
    ├── seed.py          # Database seeding
    ├── db/
    │   ├── base.py
    │   ├── models.py    # SQLAlchemy models
    │   └── session.py   # DB connection
    └── routers/
        ├── users.py     # User endpoints
        ├── rules.py     # Rule endpoints
        ├── commands.py  # Command endpoints
        └── audit.py     # Audit endpoints
```

## 🐛 Troubleshooting

### Server won't start?
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or use a different port
# Edit .env and change PORT=8000 to PORT=8001
```

### Database issues?
```powershell
# Reset database
Remove-Item command_gateway.db
python -m app.seed
```

### Package issues?
```powershell
pip install -r requirements.txt --upgrade
```

## 📝 Important Notes

- Commands are **mocked** (not actually executed) for safety
- Credits deducted only on successful execution
- All operations are transactional (all-or-nothing)
- First matching rule wins (ordered by priority)
- API keys shown only once on user creation

## 🎯 Hackathon Checklist

- [x] Backend API complete
- [x] Database with seed data
- [x] Authentication working
- [x] Rule system functional
- [x] Credit system operational
- [x] Audit logging enabled
- [ ] Frontend built
- [ ] Demo video recorded
- [ ] README updated with demo
- [ ] Deployed (optional)
- [ ] GitHub repo published

Good luck with the hackathon! 🚀
