# Minimal Token Database API

A token-optimized intelligent chatbot API that converts natural language questions into SQL queries and returns human-readable responses with minimal LLM token consumption.
Built with LangChain's native framework for universal API compatibility.

## 💡 Why Minimal Token?

### Traditional LLM Database Queries

Traditional approaches to querying databases with LLMs consume a lot of tokens:

```
Traditional Approach:
User Question (10 tokens)
  → Send entire database schema (5000+ tokens)
  → Send conversation history (2000+ tokens)
  → Get SQL query (100 tokens)
  → Send full SQL results (3000+ tokens)
  → Get formatted response (200 tokens)
────────────────────────────────────────────
Total: ~10,300+ tokens per query.
```

### Solution: Token-Optimized Architecture

**Minimal Token DB API** dramatically reduces token consumption through intelligent design:

```
Minimal Token Approach:
User Question (10 tokens)
  → Optimized schema context (200 tokens)
  → Smart conversation window (150 tokens)
  → Get SQL query (100 tokens)
  → Compressed results (500 tokens)
  → Get formatted response (200 tokens)
────────────────────────────────────────────
Total: ~1,160 tokens per query.
```

**Result: ~89% token reduction! **

### How i thinks it

1. **Selective Schema Loading**
   - Only sends relevant table descriptions based on question context
   - Eliminates unnecessary schema information
   - Dynamic schema filtering per query

2. **Conversation Memory Optimization**
   - Maintains only the last 3 Q&A pairs per session(You can change it easily)
   - Automatically prunes old context(You can desactive it)
   - Smart relevance-based history selection

3. **Result Compression**
   - Summarizes large result sets
   - Returns only essential data points
   - Intelligent data aggregation

4. **Dual-Agent Specialization**
   - Separate lightweight agents for SQL and NLP
   - Each llm receives only what it needs
   - No redundant context passing

### Universal API Compatibility

Built with **LangChain's native framework**, this architecture works with:

- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude)
- **Groq** (Llama, Mixtral, Gemma)
- **Google** (Gemini, PaLM)
- **AWS Bedrock** (Titan, Claude)
- **HuggingFace Models**

**Simply change the API key and model name**

## 🏗 Architecture

The system uses a token-optimized dual-agent architecture:

```
┌─────────────────────┐
│   User Question     │ ← 10 tokens
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│   Smart Context Builder         │
│   • Relevant schema only        │ ← 200 tokens
│   • Last 3 Q&A pairs            │ ← 150 tokens
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────┐
│   SQL Agent (LLM)   │ ← Generates MySQL query
└──────────┬──────────┘ ← 100 tokens output
           │
           ▼
┌─────────────────────┐
│   Database          │ ← Executes query
│   Execution         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│   Result Compressor             │
│   • Summarizes large sets       │ ← 500 tokens
│   • Extracts key data           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────┐
│   NLP Agent (LLM)   │ ← Formats natural language
└──────────┬──────────┘ ← 200 tokens output
           │
           ▼
┌─────────────────────┐
│   User Response     │
└─────────────────────┘

Total: ~1,160 tokens (89% reduction!)
```

### The Two Specialized Agents

1. **SQL Agent** 🔍
   - Receives only relevant schema context
   - Understands database structure
   - Generates syntactically correct MySQL queries
   - Optimizes query performance
   - Handles complex joins and aggregations

2. **NLP Agent** 💬
   - Receives only compressed results
   - Translates SQL results into natural language
   - Formats responses professionally
   - Adapts tone and style
   - Handles errors gracefully

### Token Optimization Techniques

#### 1. Dynamic Schema Loading
```python
# Instead of sending all tables (5000+ tokens)
FULL_SCHEMA = """
items: id, name, price, category, supplier_id...
stocks: id, item_id, quantity, location...
stock_movements: id, type, quantity, date...
customers: id, name, email, phone, address...
# ... 20+ more tables
"""

# We send only relevant tables (200 tokens)
RELEVANT_SCHEMA = """
items: id, name, price, stock_quantity
stocks: item_id, quantity, location
# Only 2 tables for "show items low on stock"
"""
```

#### 2. Conversation Memory Pruning
```python
# Instead of full history (2000+ tokens)
FULL_HISTORY = [
  {"q": "question 1", "a": "answer 1"},
  {"q": "question 2", "a": "answer 2"},
  # ... 10+ exchanges
]

# We keep only last 3 (150 tokens)
OPTIMIZED_HISTORY = [
  {"q": "question 8", "a": "answer 8"},
  {"q": "question 9", "a": "answer 9"},
  {"q": "question 10", "a": "answer 10"}
]
```

#### 3. Result Compression
```python
# Instead of full results (3000+ tokens)
FULL_RESULTS = [
  {"id": 1, "name": "Product A", "qty": 5, "price": 29.99, ...},
  {"id": 2, "name": "Product B", "qty": 3, "price": 19.99, ...},
  # ... 100+ rows with all columns
]

# send compressed summary (500 tokens)
COMPRESSED = {
  "total_rows": 103,
  "key_findings": ["12 items below minimum", "Total value: $15,234"],
  "sample_data": [top 3 rows with essential columns only]
}
```

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.9+** installed on your machine
- **Docker** and **Docker Compose** (recommended for deployment)
- **MySQL** or compatible database
- **LLM API Key**
## 🚀 Installation

### Option 1: Docker (Recommended) 🐳

#### 1. Clone the repository

```bash
git clone https://github.com/Rayan-ouer/minimal-token-db-api.git
cd minimal-token-db-api
```

#### 2. Create `.env` file

Create a `.env` file at the root of the project:

```env
# Database Configuration
AI_USERNAME=your_db_username
AI_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=your_database_name

# LLM API Configuration (Groq example)
GROQ_API_KEY=your_groq_api_key
AI_MODEL=llama-3.1-70b-versatile

# For OpenAI instead:
# OPENAI_API_KEY=your_openai_key
# AI_MODEL=gpt-4

# For Anthropic Claude:
# ANTHROPIC_API_KEY=your_anthropic_key
# AI_MODEL=claude-3-sonnet-20240229
```

#### 3. Launch with Docker Compose

```bash
# Build Docker image
docker compose build

# Start containers
docker compose up

# Check logs
docker compose logs
```

### Option 2: Local Installation 💻

#### 1. Clone the repository

```bash
git clone https://github.com/Rayan-ouer/minimal-token-db-api.git
cd minimal-token-db-api
```

#### 2. Create virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment (Linux/Mac)
source venv/bin/activate

# Activate environment (Windows)
venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure environment variables

Create a `.env` file as shown in Docker option.

#### 5. Launch the application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## ⚙ Configuration

### Environment Variables

```bash
# Database Configuration
AI_USERNAME=your_db_username
AI_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=your_database_name

# API Configuration
API_KEY=your_api_key
AI_MODEL=your_ai_model_name
```

*Only one API key is required

### Database Schema

The system is pre-configured for inventory management databases with tables:

- **items**: Products and commercial data
- **stocks**: Stock levels per store
- **stock_movements**: Inbound/outbound history
- **delivery_notes**: Delivery documents
- **invoices**: Issued invoices
- **customers**: Customer accounts
- **suppliers**: Supplier information
- **vehicles**: Vehicle data

#### Adapting to Your Schema

To use your own database schema:

1. Open `app/prompt/table_info.py`
2. Modify table descriptions to match your structure
3. Update example queries if necessary
4. Restart the application

### Main API Endpoint: `POST /predict`

#### Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products are out of stock?",
    "session_id": 12345
  }'
```

#### Response

```json
{
  "status": "success",
  "response": "Currently, there are 3 products out of stock: Motor Oil 5W30 (quantity: 0), K&N Air Filter (quantity: 0), and 12V 70Ah Battery (quantity: 0).",
}
```

### Request Parameters

| Parameter | Type | Description |
|-----------|------|------------
| `question` | string | Natural language question |
| `session_id` | integer | Session identifier for context |

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success - Response returned |
| `400` | Parameter validation error |
| `500` | Internal server error |

## 💡 Example Questions

```bash
# Check stock shortages
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me items below minimum stock level",
    "session_id": 1
  }'

# Total stock quantity
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total quantity of parts in stock?",
    "session_id": 1
  }'

# Stock by location
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show stock levels by warehouse location",
    "session_id": 1
  }'
```

## Project Structure

```
minimal-token-db-api/
│
├── app/                          # Main source code
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   │
│   ├── db/                       # Database management
│   │   ├── __init__.py
│   │   └── database.py           # Connection and query execution
│   │
│   ├── prompt/                   # LLM prompt configuration
│   │   ├── __init__.py
│   │   ├── prompt.py             # Templates for SQL and NLP agents
│   │   └── table_info.py         # Database schema documentation
│   │
│   ├── schemas/                  # Pydantic data models
│   │   ├── __init__.py
│   │   └── question.py           # Request/response validation
│   │
│   └── services/                 # Business logic
│       ├── __init__.py
│       ├── chat.py               # Conversation memory management
│       └── factories.py          # Agent initialization
│
├── .gitignore                    # Git ignore file
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Container orchestration
├── requirements.txt              # Python dependencies
└── README.md                     # This documentation
```

### Key Modules Description

#### `app/main.py`

FastAPI application entry point. Contains:
- CORS configuration
- Endpoint definitions
- Global error handling
- Swagger/ReDoc documentation

#### `app/db/database.py`

Database connection management:
- MySQL connection pool
- Secure SQL query execution
- Transaction handling
- Result set conversion

#### `app/prompt/prompt.py`

LLM prompt templates:
- SQL agent prompt (query generation)
- NLP agent prompt (response formatting)
- System instructions and context
- **Token optimization strategies**

#### `app/services/chat.py`

Conversation memory management:
- Per-session history storage
- Automatic pruning (last 3 exchanges only)
- Context for follow-up questions
- Memory cleanup
- **Token-efficient history management**

#### `app/services/factories.py`

Component initialization:
- LLM agent creation
- Model configuration
- Dependency injection
- **Provider-agnostic setup**

## 🔌 API Endpoints

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
  - Interactive interface to test the API
  - Detailed endpoint documentation
  - Request/response examples

- **ReDoc**: `http://localhost:8000/redoc`
  - Alternative, more readable documentation
  - API overview

### Main Endpoint

#### `POST /predict`

Processes a natural language question and returns a response.

**Request Body:**

```json
{
  "question": "string",
  "session_id": 0
}
```

**Success Response:**

```json
{
  "status": "success",
  "response": "string",
}
```

**Error Response:**

```json
{
  "status": "error",
  "response": "Error description"
}
```

### Health Check

#### `GET /health`

Checks the API health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
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

**Rayan**
- GitHub: [@Rayan-ouer](https://github.com/Rayan-ouer)
