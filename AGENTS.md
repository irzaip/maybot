# MayBot - AGENTS.md

This file contains coding guidelines, build instructions, and development information for agentic coding agents working on the MayBot WhatsApp chatbot project.

## Project Overview

MayBot is a Python-based WhatsApp chatbot system using FastAPI for web services, Ollama for AI processing, and SQLite for data storage. The bot supports multiple personas and conversation types for different use cases.

## Build & Development Commands

### Environment Setup
```bash
# Activate virtual environment
.\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start main bot service
uvicorn wa:app --port 8998 --host 192.168.30.50

# Alternative startup using batch file
maya_be.bat

# Full startup script (includes Node.js services)
run.bat
```

### Linting & Code Quality
```bash
# Run ruff linter (available in requirements.txt)
python -m ruff check .

# Auto-fix issues with ruff
python -m ruff check --fix .

# Run ruff formatter (if configured)
python -m ruff format .
```

### Testing
```bash
# Run the single test file
python test_agent.py

# Test individual functions (no formal test framework)
# Manually test endpoints using curl/requests:
curl http://192.168.30.50:8998/ping
curl http://192.168.30.50:8998/test_send/6285775300227@c.us
```

### Database Operations
```bash
# Database file: cipibot.db
# Schema defined in cr.sql
# Use SQLite CLI or db_oper.py functions for operations
```

## Code Style Guidelines

### Python Standards
- **Python Version**: 3.11+
- **Code Style**: PEP 8 (enforced by ruff)
- **Line Length**: 88 characters (ruff default)
- **Import Style**: Use `isort`-style imports (ruff handles this)

### Import Organization
```python
# Standard library imports first
import os
import sys
from typing import List, Union

# Third-party imports second
import toml
import requests
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# Local imports third
from conversations import Message, Persona
from db_oper import insert_conv
```

### Type Hints
- **Required**: All function parameters and return types must have type hints
- **Models**: Use Pydantic BaseModel for data validation
- **Enums**: Use str-based Enums for configuration constants

```python
from typing import List, Union, Dict, Optional
from pydantic import BaseModel

def process_message(msg: str, user_id: str) -> Optional[Dict[str, str]]:
    """Process incoming message and return response dict."""
    pass

class MessageData(BaseModel):
    content: str
    user_number: str
    timestamp: int
```

### Naming Conventions
- **Variables**: snake_case (e.g., `user_number`, `message_content`)
- **Functions**: snake_case with descriptive names (e.g., `process_conversation`)
- **Classes**: PascalCase (e.g., `MessageProcessor`, `ConversationHandler`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_TOKEN_LIMIT`, `BOT_NUMBER`)
- **Files**: snake_case (e.g., `conversations.py`, `db_oper.py`)

### Error Handling
```python
# Use specific exception handling
try:
    result = await api_call()
except requests.ConnectionError:
    logger.error("Failed to connect to API")
    return {"error": "Connection failed"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}
```

### Configuration Management
- **Config File**: Use `config.toml` for all configuration
- **Loading**: `cfg = toml.load('config.toml')`
- **Access**: `cfg['SECTION']['KEY']` pattern

### Database Patterns
- **Connection**: Use context managers or explicit close()
- **Operations**: Separate functions in `db_oper.py`
- **Type Safety**: Use SQLite type hints when available

### FastAPI Patterns
```python
from fastapi import FastAPI, HTTPException, Depends

@app.get("/endpoint/{param}")
async def get_endpoint(param: str) -> Dict[str, str]:
    """Endpoint description."""
    if not param:
        raise HTTPException(status_code=400, detail="Parameter required")
    return {"result": f"Processed {param}"}
```

### Async/Await Usage
- **API Calls**: Use async/await for all HTTP requests
- **Database**: Keep DB operations synchronous (SQLite limitation)
- **Concurrency**: Use asyncio for concurrent processing

### Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=cfg['CONFIG']['LOGDIR'] + 'app.log'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

## Project Structure

### Core Components
- **`wa.py`**: Main FastAPI application and WhatsApp integration
- **`conversations.py`**: Data models and conversation management
- **`ollama_api.py`**: AI/LLM integration using Ollama
- **`db_oper.py`**: Database operations and SQLite management
- **`config.toml`**: Application configuration and persona definitions

### Agent Files
- **`agent[1-8].py`**: Specialized agent implementations
- **`persona_func.py`**: Persona management functions
- **`conv_func.py`**: Conversation processing utilities

### Supporting Modules
- **`Msgproc.py`**: Message processing logic
- **`reduksi.py`**: Text reduction/token management
- **`trans_id.py`**: Transaction/ID handling
- **`counting.py`**: Usage tracking and analytics

## Development Workflow

1. **Before coding**: Run `python -m ruff check .` to see current issues
2. **During development**: Use `python -m ruff check --fix .` frequently
3. **Before commits**: Ensure all ruff issues are resolved
4. **Testing**: Run `python test_agent.py` and manual endpoint testing
5. **Database changes**: Update `cr.sql` schema accordingly

## Key Dependencies
- **FastAPI**: Web framework and API endpoints
- **Ollama**: Local AI/LLM integration
- **Pydantic**: Data validation and settings
- **SQLite**: Database storage
- **Requests**: HTTP client for external APIs
- **Ruff**: Linting and formatting (already in requirements.txt)

## Testing Strategy
- No formal testing framework currently used
- Manual testing via `test_agent.py` and HTTP endpoints
- Test functions are integrated into main application
- Use `test_send/` endpoint for manual message testing

## Notes for Agents
- This is a WhatsApp bot project - be mindful of message processing workflows
- The codebase uses Indonesian language in comments and configurations
- Multiple personas are configured - check `config.toml` for persona definitions
- Database operations are synchronous due to SQLite limitations
- Always verify configuration changes don't break existing persona workflows