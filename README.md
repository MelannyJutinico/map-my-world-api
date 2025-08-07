# Map My World API

Map My World is a geolocation API developed in FastAPI that allows users to register and classify locations using either manual or AI-powered categorization. Designed for real-world scalability, this system leverages NLP, reverse geocoding, and intelligent prioritization for location review workflows.

## Key Features


- **Location & Category Management**  
  - Create, read, update and delete locations and categories.  
  - When you POST a new location you can supply:
    - `category_ids`: list of existing category IDs, **or**
    - `description`: free-text for NLP inference of category.  
  - Automatically enrich location data using reverse geocoding (OpenCageData) to retrieve address, city, and country.

- **AI-powered Classification**  
  - Uses Hugging Face’s `facebook/bart-large-mnli` zero-shot model to infer categories using BART-MNLI NLP model when no category is provided.


- **Recommendation Engine**  
  - Scores every location-category combination:
    - **100** for never-reviewed items  
    - **days_since_last_review × 2** (capped at 100) for items reviewed over 30 days ago  
  - Returns the top N combinations that need a fresh review.

- **Clean Architecture**  
  - **Routers** for HTTP layer  
  - **Services** for business logic  
  - **Repositories** for data access  
  - **Schemas** (Pydantic) for validation & docs  
  - **Utils** for geocoding and NLP  

- **CORS & Settings**  
  - Configurable via environment variables  
  - CORS origins defined in `ALLOWED_ORIGINS`  

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (Async)
- SQLite (local)
- OpenCageData API (Reverse Geocoding)
- Hugging Face Transformers (NLP Classification)
- HTTPX for async HTTP calls
- OpenCageData API for reverse geocoding  
  
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
│   ├── services/
│   │   ├── category_service.py
│   │   ├── location_service.py
│   │   ├── recommendation_service.py
│   │   └── review_service.py
│   └── utils/
│       ├── geocoding.py                # Integration with OpenCage API
│       └── nlp.py                      # Classification using Hugging Face models
├── db/
│   ├── repositories/
│   │   ├──category_repository.py      # Category DB operations
│   │   └── location_repository.py      # Location DB operations
│   └──session.py           # Engine & session factory
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
    OPENCAGE_API_KEY=your_opencage_key
    DATABASE_URL=sqlite:///./mapmyworld.db
    ALLOWED_ORIGINS=http://localhost:3000,http://localhost
    ```

4. Start the app:
    ```bash
    uvicorn app.main:app --reload
    ```



The system ensures relevant and timely suggestions by dynamically prioritizing what's due for review.

## API Docs

FastAPI automatically generates docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Author

Melanny Jutinico — AI & Automation Developer

---

This project was built as part of a backend challenge focused on geospatial intelligence, smart recommendations, and natural language processing integration.
