# Video Processing and Analysis Backend

A scalable backend system for video processing and frame analysis using FastAPI, OpenCV, and Streamlit.

## Features

- Video upload and YouTube video download capabilities
- Frame extraction every 10 seconds using OpenCV
- Clean architecture with Controller-Service-Model pattern
- FastAPI-based RESTful API
- Streamlit dashboard for user interaction
- Docker support for easy deployment

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── controllers/
│   │   ├── dependencies/
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── domain/
│   │   └── schemas/
│   ├── services/
│   │   ├── video/
│   │   └── frame/
│   └── utils/
├── frontend/
│   └── streamlit_app.py
├── tests/
├── storage/
│   ├── videos/
│   └── frames/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables
5. Run the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Run the Streamlit frontend (in a new terminal):
   ```bash
   # Make sure you're in the project root and your virtual environment is activated
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```
   The Streamlit dashboard will be available at: `http://localhost:8501`

Note: Make sure both the FastAPI backend (port 8000) and Streamlit frontend (port 8501) are running simultaneously for the application to work properly.

## Docker Deployment

Build and run using Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests using pytest:
```bash
pytest
```

## License

MIT License 