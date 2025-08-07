# Map My World API

Map My World is a geolocation API developed in FastAPI that allows users to register and classify locations using either manual or AI-powered categorization. Designed for real-world scalability, this system leverages NLP, reverse geocoding, and intelligent prioritization for location review workflows.

## Key Features

- **Location & Category Management**: 
  - Create locations with coordinates and optional description or category IDs.
  - Automatically enrich location data using reverse geocoding (OpenCageData) to retrieve address, city, and country.
  - Classify locations with relevant categories using BART-MNLI NLP model when no category is provided.

- **Recommendation Engine**:
  - Scores combinations of locations and categories.
  - Prioritizes places never reviewed or not reviewed in over 30 days.
  - Custom logic to balance novelty and time relevance.

- **Clean Architecture**:
  - Separated concerns: routers, services, schemas, and repositories.
  - Asynchronous support using FastAPI and HTTPX.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL / SQLite (local)
- OpenCageData API (Reverse Geocoding)
- Hugging Face Transformers (NLP Classification)
- HTTPX for async HTTP calls

  
## Folder Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── categories.py           # Endpoints for managing categories
│           ├── locations.py            # Endpoints for managing locations
│           ├── recommendations.py      # Endpoints for recommending locations
│           └── reviews.py              # Endpoints to record location reviews
├── core/
│   ├── models/
│   │   ├── database.py                 # SQLAlchemy DB engine and base
│   │   └── schemas.py                  # Pydantic schemas
│   └── utils/
│       ├── geocoding.py                # Integration with OpenCage API
│       └── nlp.py                      # Classification using Hugging Face models
├── db/
│   └── repositories/
│       ├── category_repository.py      # Category DB operations
│       └── location_repository.py      # Location DB operations
├── main.py                             # FastAPI app entry point
└── config.py                           # Environment variable settings
```



## How to Run

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/map-my-world-api.git
    cd map-my-world-api
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file and configure your API key:
    ```env
    OPENCAGE_API_KEY=your_key_here
    ```

4. Start the app:
    ```bash
    uvicorn app.main:app --reload
    ```

## Smart Categorization

When a user provides a textual description, the API uses the `facebook/bart-large-mnli` model to infer the most suitable category based on semantic similarity with available options.

## Recommendation Scoring Logic

- **Score 100**: Never reviewed combinations.
- **Score = days since last review × 2**: For combinations reviewed over 30 days ago.

The system ensures relevant and timely suggestions by dynamically prioritizing what's due for review.

## API Docs

FastAPI automatically generates docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Author

Melanny Jutinico — AI & Automation Developer

---

This project was built as part of a backend challenge focused on geospatial intelligence, smart recommendations, and natural language processing integration.