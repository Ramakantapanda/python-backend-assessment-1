# Python Backend Engineer Take Home Assessment

## Problem Understanding & Assumptions

### Interpretation
I interpreted the core requirements as building a robust REST API service using FastAPI and PostgreSQL that acts as a bridge between a local database and an external API. The service needed to demonstrate complex data flows, strict validation, and proper testing.

### Use Case: "AI-Powered Task Summarizer"
The API serves as a bridge between a local task management system and an external API (simulated with JSONPlaceholder). It allows users to manage tasks locally while also fetching related data from external sources to enhance the local records.

### Assumptions
- **Data Formats**: I assumed that the external API would return JSON data, which would be stored as text in the local database
- **External API Reliability**: I assumed the external API might occasionally fail, so implemented retry logic and proper error handling
- **User Authentication**: For simplicity in this assessment, I focused on the core API functionality without authentication, though in production this would be required
- **Business Logic Constraints**: I assumed that external data fetched from the API should be stored separately from the original item data to maintain data integrity

## Design Decisions

### Database Schema
- **Items Table**: Contains `id`, `title`, `description`, `external_data`, `created_at`, and `updated_at` fields
- **Indexing**: Added indexes on `id` and `title` for efficient querying
- **Timestamps**: Included both `created_at` and `updated_at` for audit trails

### Project Structure
I used a layered architecture approach:
- `app/`: Main application package
  - `database/`: Database configuration and session management
  - `models/`: SQLAlchemy models
  - `schemas/`: Pydantic validation schemas
  - `routes/`: API route handlers
  - `utils/`: Utility functions and services

### Validation Logic
- Used Pydantic models for both request bodies and response schemas
- Implemented strict validation at the API level
- Ensured data integrity beyond basic type checking by validating required fields

### External API Design
- Implemented timeout handling (10 seconds)
- Added retry mechanism with exponential backoff for rate limits
- Used proper error handling for connection issues, timeouts, and API failures
- Created a service class to encapsulate external API logic

## Solution Approach

### Data Flow
1. **POST /api/v1/items**: Client sends item data → validation → stored in PostgreSQL
2. **GET /api/v1/items/{id}**: Client requests item → fetch from PostgreSQL → return to client
3. **PUT /api/v1/items/{id}**: Client sends update → validation → update in PostgreSQL
4. **DELETE /api/v1/items/{id}**: Client requests deletion → remove from PostgreSQL
5. **GET /api/v1/external/fetch-data/{id}**: Client requests external data → fetch from external API → merge with local data → store in PostgreSQL

## Error Handling Strategy

### Failure Management
- **DB Connection**: Implemented try-catch blocks with rollbacks for database transactions
- **3rd-party API Downtime**: Added timeout handling, retry logic, and appropriate HTTP status codes (502 for gateway errors)
- **Input Validation**: Used Pydantic for automatic validation and return 422 for unprocessable entities

### Global Exception Handling
- Used FastAPI's built-in HTTPException for consistent error responses
- Implemented proper HTTP status codes (201 for created, 404 for not found, 422 for validation errors, etc.)

## How to Run the Project

### Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Required Environment Variables (.env.example)
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
PORT=8000
```

### Example API Calls

#### Create an item
```bash
curl -X POST "http://localhost:8000/api/v1/items" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "description": "This is a sample task"}'
```

#### Get an item
```bash
curl -X GET "http://localhost:8000/api/v1/items/1"
```

#### Update an item
```bash
curl -X PUT "http://localhost:8000/api/v1/items/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "description": "This is an updated task"}'
```

#### Delete an item
```bash
curl -X DELETE "http://localhost:8000/api/v1/items/1"
```

#### Fetch external data for an item
```bash
curl -X GET "http://localhost:8000/api/v1/external/fetch-data/1"
```

#### Get external posts
```bash
curl -X GET "http://localhost:8000/api/v1/external/posts"
```

The API documentation is automatically available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).