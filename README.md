# Command Gateway - Backend API

A FastAPI-based command execution gateway with rule-based access control, credit system, and comprehensive audit logging.

## 🎯 Overview

The Command Gateway is a system where administrators configure rules to control which commands can run. Safe commands execute automatically, dangerous commands get blocked, and everything is tracked with a credit system and audit trail.

## ✨ Features

- **API Key Authentication**: Simple authentication using API keys in request headers
- **Role-Based Access Control**: Admin and Member roles with different permissions
- **Command Credit System**: Track and manage user credits for command execution
- **Rule-Based Command Filtering**: Regex-based rules with AUTO_ACCEPT, AUTO_REJECT, and REQUIRE_APPROVAL actions
- **Transaction Safety**: All operations (credit deduction, execution, logging) succeed or fail together
- **Comprehensive Audit Logging**: Complete trail of all actions in the system
- **RESTful API**: Well-structured endpoints for all operations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd comman-gateway-be
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env if needed (default SQLite configuration works out of the box)
```

5. Initialize the database and seed data:
```bash
python -m app.seed
```

This will create:
- A default admin user (username: `admin`)
- Default rules for dangerous and safe commands
- Display the admin API key (save this!)

6. Start the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## 🔑 Authentication

All API requests (except `/` and `/health`) require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY_HERE" http://localhost:8000/users/me
```

## 📋 API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check

### User Endpoints
- `POST /users/` - Create a new user (Admin only)
- `GET /users/me` - Get current user info
- `GET /users/me/stats` - Get current user's statistics
- `GET /users/me/commands` - Get current user's command history
- `GET /users/` - List all users (Admin only)
- `PATCH /users/{user_id}/credits` - Update user credits (Admin only)

### Rule Endpoints
- `POST /rules/` - Create a new rule (Admin only)
- `GET /rules/` - List all rules
- `GET /rules/{rule_id}` - Get a specific rule
- `PUT /rules/{rule_id}` - Update a rule (Admin only)
- `DELETE /rules/{rule_id}` - Delete a rule (Admin only)

### Command Endpoints
- `POST /commands/` - Submit a command for execution
- `GET /commands/` - Get current user's command history
- `GET /commands/{command_id}` - Get a specific command

### Audit Endpoints
- `GET /audit/` - Get audit logs (Admin only)
- `GET /audit/user/{user_id}` - Get audit logs for a specific user (Admin only)

## 🎮 Usage Examples

### 1. Get Current User Info

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/users/me
```

Response:
```json
{
  "username": "admin",
  "role": "admin",
  "id": 1,
  "credits": 1000,
  "created_at": "2025-12-11T10:00:00"
}
```

### 2. Submit a Safe Command

```bash
curl -X POST http://localhost:8000/commands/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command_text": "ls -la"}'
```

Response:
```json
{
  "id": 1,
  "command_text": "ls -la",
  "status": "executed",
  "credits_deducted": 1,
  "result": "[MOCK] Command 'ls -la' would be executed with status: SUCCESS",
  "submitted_at": "2025-12-11T10:05:00",
  "executed_at": "2025-12-11T10:05:00",
  "rule_id": 7
}
```

### 3. Submit a Dangerous Command

```bash
curl -X POST http://localhost:8000/commands/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command_text": "rm -rf /"}'
```

Response:
```json
{
  "id": 2,
  "command_text": "rm -rf /",
  "status": "rejected",
  "credits_deducted": 0,
  "result": "Command rejected by rule: Delete root directory - extremely dangerous",
  "submitted_at": "2025-12-11T10:06:00",
  "executed_at": null,
  "rule_id": 2
}
```

### 4. Create a New Rule (Admin)

```bash
curl -X POST http://localhost:8000/rules/ \
  -H "X-API-Key: ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "^sudo\s+",
    "action": "AUTO_REJECT",
    "description": "Sudo commands require elevation",
    "priority": 0
  }'
```

### 5. Create a New User (Admin)

```bash
curl -X POST http://localhost:8000/users/ \
  -H "X-API-Key: ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "role": "member"
  }'
```

Response (includes one-time API key):
```json
{
  "id": 2,
  "username": "john_doe",
  "role": "member",
  "credits": 100,
  "created_at": "2025-12-11T10:10:00",
  "api_key": "abc123..."
}
```

### 6. View Audit Logs (Admin)

```bash
curl -H "X-API-Key: ADMIN_API_KEY" http://localhost:8000/audit/
```

## 🔐 Default Rules

The system comes pre-configured with these rules:

| Priority | Pattern | Action | Description |
|----------|---------|--------|-------------|
| 0 | `:(){ :\|:& };:` | AUTO_REJECT | Fork bomb - dangerous recursive process |
| 0 | `rm\s+-rf\s+/` | AUTO_REJECT | Delete root directory - extremely dangerous |
| 0 | `mkfs\.` | AUTO_REJECT | Format filesystem - data loss |
| 0 | `dd\s+if=/dev/(zero\|random)\s+of=/dev/` | AUTO_REJECT | Overwrite disk - data loss |
| 0 | `chmod\s+-R\s+777\s+/` | AUTO_REJECT | Make all files world-writable - security risk |
| 1 | `git\s+(status\|log\|diff\|branch\|show)` | AUTO_ACCEPT | Safe git read operations |
| 1 | `^(ls\|cat\|pwd\|echo\|which\|whoami\|date\|uptime)` | AUTO_ACCEPT | Safe basic commands |
| 1 | `^grep\s+` | AUTO_ACCEPT | Text search - safe |
| 1 | `^find\s+` | AUTO_ACCEPT | File search - safe |

**Note**: Lower priority number = higher priority. First match wins!

## 🏗️ Project Structure

```
comman-gateway-be/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── app/
    ├── __init__.py
    ├── dependencies.py    # Authentication and dependencies
    ├── schemas.py         # Pydantic models for request/response
    ├── utils.py           # Utility functions
    ├── seed.py            # Database seeding script
    ├── db/
    │   ├── __init__.py
    │   ├── base.py        # SQLAlchemy base
    │   ├── models.py      # Database models
    │   └── session.py     # Database session configuration
    └── routers/
        ├── __init__.py
        ├── users.py       # User management endpoints
        ├── rules.py       # Rule management endpoints
        ├── commands.py    # Command submission endpoints
        └── audit.py       # Audit log endpoints
```

## 💡 Key Design Decisions

### 1. Transaction Safety
All command executions use database transactions to ensure atomicity. If credit deduction fails, the command isn't executed. If execution logging fails, credits aren't deducted. This prevents inconsistent state.

### 2. First Match Wins
When a command is submitted, it's checked against rules ordered by priority (lower number = higher priority). The first matching rule determines the action.

### 3. Mock Execution
Commands are not actually executed on the server for safety. Instead, they're logged as "would be executed". This is perfect for demonstration and testing.

### 4. API Key Authentication
Simple header-based authentication (`X-API-Key`) makes it easy to integrate with any client (CLI, web app, mobile app).

### 5. Regex Validation
All rule patterns are validated as proper regex before saving. Invalid patterns are rejected with helpful error messages.

## 🧪 Testing

You can test the API using:

1. **Interactive Swagger UI**: http://localhost:8000/docs
2. **curl** (see examples above)
3. **Postman** or any API client
4. **Python requests library**:

```python
import requests

API_KEY = "your_api_key_here"
headers = {"X-API-Key": API_KEY}

# Get user info
response = requests.get("http://localhost:8000/users/me", headers=headers)
print(response.json())

# Submit command
response = requests.post(
    "http://localhost:8000/commands/",
    headers=headers,
    json={"command_text": "ls -la"}
)
print(response.json())
```

## 📊 Database Schema

### Users
- `id`: Integer, Primary Key
- `username`: String, Unique
- `api_key`: String, Unique
- `role`: Enum (admin, member)
- `credits`: Integer
- `created_at`: DateTime

### Rules
- `id`: Integer, Primary Key
- `pattern`: String (regex)
- `action`: Enum (AUTO_ACCEPT, AUTO_REJECT, REQUIRE_APPROVAL)
- `description`: String
- `priority`: Integer
- `created_at`: DateTime
- `created_by`: Foreign Key → Users

### Commands
- `id`: Integer, Primary Key
- `command_text`: Text
- `status`: Enum (accepted, rejected, executed, pending_approval)
- `user_id`: Foreign Key → Users
- `rule_id`: Foreign Key → Rules
- `credits_deducted`: Integer
- `result`: Text
- `submitted_at`: DateTime
- `executed_at`: DateTime

### AuditLog
- `id`: Integer, Primary Key
- `user_id`: Foreign Key → Users
- `action`: String
- `details`: Text (JSON)
- `timestamp`: DateTime

## 🚀 Deployment

### Using Render, Railway, or Fly.io

1. Set `DATABASE_URL` environment variable to your PostgreSQL database
2. Update `requirements.txt` to include `psycopg2-binary` for PostgreSQL
3. Deploy using their CLI or web interface

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t command-gateway .
docker run -p 8000:8000 command-gateway
```

## 🎁 Bonus Features

The codebase is structured to easily add these bonus features:

1. **REQUIRE_APPROVAL**: Already supported in models and schemas. Commands with this action get `pending_approval` status.
2. **Notifications**: Add email/Telegram integration in `commands.py` when creating approval requests.
3. **Rule Conflict Detection**: Add validation in `rules.py` to check pattern overlaps before creation.
4. **Voting Thresholds**: Extend `Rule` model with `approval_threshold` field.
5. **Time-Based Rules**: Add time checking logic in `match_command_against_rules()`.

## 📝 License

MIT License - feel free to use this for the hackathon and beyond!

## 🤝 Contributing

This is a hackathon project, but contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📞 Support

For questions or issues, please create an issue in the GitHub repository.

---

**Built with ❤️ for Unbound Hackathon**
