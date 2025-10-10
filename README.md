# AZ Chat Bot 

An intelligent chatbot that converts natural language questions into SQL queries and returns human-readable responses. Built specifically for inventory and stock management systems.

## Features

- **Natural Language to SQL**: Converts business questions into MySQL queries using LLM
- **Dual-Agent Architecture**: Separate agents for SQL generation and response formatting
- **Conversation Memory**: Maintains context across multiple questions per session
- **Database Agnostic**: Works with any SQL database schema
- **Docker Ready**: Fully containerized for easy deployment
- **Session Management**: Handles multiple concurrent user sessions

## Architecture

```
User Question
     ↓
SQL Agent (Groq LLM) → Generates MySQL Query
     ↓
Database Execution → Returns Raw Data
     ↓
NLP Agent (Groq LLM) → Formats Human Response
     ↓
User Response
```

**Two-Agent System:**
1. **SQL Agent**: Understands database schema and generates syntactically correct MySQL queries
2. **NLP Agent**: Translates raw SQL results into clear, professional French responses

## Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- MySQL Database
- Groq API Key ([Get one here](https://console.groq.com/))

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/Rayan-ouer/AZ-chat-bot.git
cd AZ-chat-bot
```

2. **Create `.env` file**
```bash
# Database Configuration
AI_USERNAME=your_db_username
AI_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=your_database_name

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
AI_MODEL=llama-3.1-70b-versatile
```

3. **Run with Docker Compose**
```bash
docker compose build
docker compose up
```

4. **Access the API**
```
http://localhost:8000/docs
```

### Option 2: Local Development

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables** (create `.env` file as shown above)

3. **Run the application**
```bash
uvicorn app.main:app --reload --port 8000
```

## API Usage

### Endpoint: `POST /predict`

**Request Body:**
```json
{
  "question": "Quels produits sont en rupture de stock?",
  "session_id": 12345
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Actuellement, il y a 3 produits en rupture de stock : Huile moteur 5W30 (quantité: 0), Filtre à air K&N (quantité: 0), et Batterie 12V 70Ah (quantité: 0)."
}
```

### Example Questions

```bash
# Stock status
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me items below minimum stock",
    "session_id": 1
  }'

# Sales analysis
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 5 selling products this month?",
    "session_id": 1
  }'

# Inventory check
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which suppliers have outstanding balances?",
    "session_id": 1
  }'
```

## Project Structure

```
AZ-chat-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── db/
│   │   ├── database.py         # Database connection and query execution
│   │   └── __init__.py
│   ├── prompt/
│   │   ├── prompt.py           # LLM prompts for SQL and NLP agents
│   │   ├── table_info.py       # Database schema documentation
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── question.py         # Pydantic models
│   │   └── __init__.py
│   └── services/
│       ├── chat.py             # Memory and conversation management
│       ├── factories.py        # Agent initialization
│       └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

### Database Schema

The bot is pre-configured for inventory management systems with tables for:
- **items**: Products and commercial data
- **stocks**: Stock levels per store
- **stock_movements**: Inbound/outbound history
- **delivery_notes**: Delivery documents
- **invoices**: Issued invoices
- **customers**: Customer accounts
- **suppliers**: Supplier information
- **vehicles**: Vehicle data

To adapt to your schema, modify `app/prompt/table_info.py`.

### LLM Models

Supported Groq models:
- `llama-3.1-70b-versatile` (recommended)
- `mixtral-8x7b-32768`
- `gemma-7b-it`

Change the model in your `.env` file:
```bash
AI_MODEL=llama-3.1-70b-versatile
```

### Memory Management

Conversation history is automatically managed:
- Keeps last 3 Q&A pairs per session
- Prevents memory overflow
- Maintains context for follow-up questions

## Testing

Example test queries in various languages:

**French:**
- "Quels sont les produits en rupture de stock ?"
- "Donne-moi le chiffre d'affaires du mois dernier"
- "Liste les clients avec un risque élevé"

**English:**
- "Show me items below minimum stock"
- "What's the total revenue for this year?"
- "Which vehicles need maintenance?"

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is accessible
mysql -h DB_HOST -u AI_USERNAME -p
```

### Groq API Errors
```bash
# Verify API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

### Docker Issues
```bash
# Rebuild containers
docker compose down
docker compose build
docker compose up

# View logs
docker compose logs -f
```

## Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework
- **[LangChain](https://python.langchain.com/)**: LLM orchestration
- **[Groq](https://groq.com/)**: LLM inference
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: Database ORM
- **[Pydantic](https://pydantic.dev/)**: Data validation
- **[Docker](https://www.docker.com/)**: Containerization

## Author

**Rayan**
- GitHub: [@Rayan-ouer](https://github.com/Rayan-ouer)

## Acknowledgments

- Built with [Groq](https://groq.com/) for lightning-fast LLM inference
- Powered by [LangChain](https://python.langchain.com/) for agent orchestration
- Inspired by the need for accessible database querying

---
