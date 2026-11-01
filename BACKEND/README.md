# KrishiDrishti Backend

AI-powered crop disease detection and advisory platform — FastAPI backend.

## Prerequisites

- Python 3.12+
- Node.js 18+ (for the frontend in `../FRON`)

## Quick start

```bash
# 1. Create and activate a virtual environment
cd BACKEND
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env from the example
copy .env.example .env
# Edit .env and set a real SECRET_KEY:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"

# 4. Initialise the database and load seed data
python -m app.db.init_db

# 5. Start the backend
uvicorn app.main:app --reload
```

API is now available at **http://127.0.0.1:8000**

Interactive docs: **http://127.0.0.1:8000/docs**

## Environment variables

See `.env.example` for all available settings. The most important ones:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/krishidrishti.db` | Database connection |
| `SECRET_KEY` | *(must change)* | JWT signing key |
| `MODEL_PATH` | *(empty)* | Path to a real trained model; leave blank to use mock |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

## Running tests

```bash
pytest
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Service health check |
| POST | `/api/auth/signup` | Register a new farmer |
| POST | `/api/auth/login` | Login → JWT token |
| POST | `/api/auth/logout` | Logout (client discards token) |
| GET | `/api/users/me` | Get current user profile |
| PATCH | `/api/users/me` | Update profile / password |
| GET | `/api/crops` | List supported crops |
| GET | `/api/crops/{id}` | Crop detail |
| GET | `/api/diseases` | List diseases |
| GET | `/api/diseases/{id}` | Disease detail (with language support) |
| GET | `/api/advisories/{id}` | Disease advisory content |
| POST | `/api/scans` | Upload image → run prediction |
| GET | `/api/scans` | List user's scans |
| GET | `/api/scans/{id}` | Scan detail |
| DELETE | `/api/scans/{id}` | Delete a scan |
| POST | `/api/feedback` | Submit prediction feedback |
| POST | `/api/expert-requests` | Request expert review |
| GET | `/api/expert-requests` | List expert requests |
| POST | `/api/sync` | Sync offline records |

## AI model integration

The backend currently uses a **mock prediction service**. To integrate a real model:

1. Train a crop disease classification model (TensorFlow/Keras recommended).
2. Save the model weights/SavedModel to `ml/model/`.
3. Set `MODEL_PATH=ml/model/your_model.h5` in `.env`.
4. Replace `ml/labels.json` with your model's label mapping.
5. Adjust `ml/preprocessing.py` to match your model's expected input.
6. Install TensorFlow: `pip install tensorflow`.

The `MockPredictionService` in `app/services/prediction_service.py` is clearly labeled — it produces deterministic demo predictions based on image statistics, not real AI inference.

## Known limitations

- No trained model is included. All predictions are demo/mock results.
- SQLite is used for development. Switch `DATABASE_URL` to PostgreSQL for production.
- JWT tokens cannot be revoked before expiry without implementing a blacklist.
- Disease advisory content is demonstration data. All advisory text requires review by a qualified agricultural expert before production use.
- Offline inference is not supported from the backend. The device must be online to submit scans.

## Deployment notes

- Use a PostgreSQL database in production.
- Set `DEBUG=False` and use a strong `SECRET_KEY`.
- Set `CORS_ORIGINS` to your production frontend URL only.
- Use a reverse proxy (nginx) in front of uvicorn.
- Store uploaded images on object storage (e.g., S3) in production.
