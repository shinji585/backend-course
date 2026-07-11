# Backend Course — Tracked Products API

A small FastAPI service for tracking products (e.g. price-tracking a laptop or phone) with tag-based organization. Built as a learning project to practice a clean **repository / service / router** architecture, Pydantic schemas, and REST API design with FastAPI.

> Note: Currently uses flat JSON files as storage (no database yet) — see [Architecture](#architecture) below.

---

## Features

- Create, retrieve, update, and delete tracked products
- Attach one or more tags to a tracked product (tags are created automatically if they don't exist yet)
- Paginated product listing (`limit` / `offset`)
- Partial updates via `PATCH` (only sent fields are modified)
- Clean separation between HTTP layer, business logic, and persistence
- Fully typed with Pydantic v2 schemas and Python type hints

---

## Tech Stack

- **Python 3.14**
- **FastAPI** — web framework / routing / OpenAPI docs
- **Pydantic v2** — schema validation and serialization
- **uv** — dependency management (`pyproject.toml`, `uv.lock`)
- JSON files as the current storage backend (`app/db/data/`)

---

## Project Structure

```
app/
├── core/
│   └── logging.py              # Centralized logger configuration
├── db/
│   ├── data/                   # JSON "database" files
│   │   ├── tagsData.json
│   │   └── TrackedProduct.json
│   ├── migrations/             # Reserved for future DB migrations
│   ├── repositories/
│   │   ├── tag_repository.py           # Tag persistence (CRUD over JSON)
│   │   └── tracked_product_repository.py
│   └── database.py
├── models/                     # (Reserved for future ORM models)
├── routers/                    # FastAPI route definitions (HTTP layer)
├── schemas/
│   ├── enums/                  # currency.py, status.py, tags.py
│   ├── price/                  # Price value object
│   ├── tags/                   # base / internal / public / update tag schemas
│   ├── tracked/                # base / create / internal / public / update schemas
│   └── users/
├── services/
│   ├── tags.py                 # Tag business logic
│   ├── trackedProduct.py       # Tracked product business logic
│   └── users.py
├── deps.py                     # FastAPI dependency providers (Depends)
├── main.py                     # App entrypoint
└── logger/
    └── application.log

tests/

Dockerfile
docker-compose.yml
pyproject.toml
uv.lock
```

### Architecture

The project follows a **three-layer** design:

1. **Router (`app/routers/`)** — Handles HTTP concerns only: request/response models, status codes, path/query parameters, and translating service results into `HTTPException`s.
2. **Service (`app/services/`)** — Business logic: validation, coordinating between tags and tracked products, deciding what counts as success/failure.
3. **Repository (`app/db/repositories/`)** — Persistence only: reading/writing the JSON files, versioning, backups on corruption. Exposes a small CRUD-style interface (`find_all`, `find_by_id`, `save`, `update`, `delete`) so the storage backend can be swapped later (e.g. for a real database) without touching the service or router layers.

Dependency wiring for FastAPI's `Depends()` lives in `app/deps.py`, which constructs services with their concrete config paths and caches them as singletons via `@lru_cache`.

---

## Getting Started

### Prerequisites

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) installed

### Installation

```bash
git clone https://github.com/shinji585/backend-course.git
cd backend-course
uv sync
```

### Running the app

```bash
uv run python -m app.main
```

or, if you're serving via `uvicorn` directly:

```bash
uv run uvicorn app.main:app --reload
```

Once running, interactive API docs are available at:

- Scalar: `http://localhost:8000/scalar` (preferred — cleaner UI, used for this project)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Running with Docker

The project includes a `Dockerfile` and `docker-compose.yml` for containerized setup.

```bash
docker compose up --build
```

This builds the image and starts the API container. Once running, the docs are available the same way as a local run:

- Scalar: `http://localhost:8000/scalar`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

To stop the container:

```bash
docker compose down
```

> Check `docker-compose.yml` for the exact port mapping and any environment variables it expects — adjust the URLs above if the exposed port differs.

---

## API Overview

Base path: `/trackedProducts`

| Method   | Path                        | Description                                      |
|----------|-----------------------------|---------------------------------------------------|
| `POST`   | `/trackedProducts/`         | Create a new tracked product                      |
| `GET`    | `/trackedProducts/`         | List tracked products (paginated)                  |
| `GET`    | `/trackedProducts/{id}`     | Retrieve a single tracked product by ID            |
| `PATCH`  | `/trackedProducts/{id}`     | Partially update a tracked product                 |
| `DELETE` | `/trackedProducts/{id}`     | Delete a tracked product                           |

### Create a tracked product

```
POST /trackedProducts/
```

**Body** (`TrackedProductCreate`):

```json
{
  "name": "Lenovo Legion Pro 7",
  "description": "16-inch gaming laptop with RTX 5080, 32 GB RAM, and 2 TB SSD.",
  "quantity": 1,
  "target_price": { "amount": 1800, "currency": "USD" },
  "tags_name": [{ "name": "Gaming" }, { "name": "Work" }]
}
```

**Responses**

| Status | Meaning                                   |
|--------|--------------------------------------------|
| `201`  | Tracked product created successfully        |
| `400`  | Tracked product could not be created         |
| `500`  | Unexpected server error                      |

### List tracked products

```
GET /trackedProducts/?limit=20&offset=0
```

| Query param | Default | Description                          |
|-------------|---------|----------------------------------------|
| `limit`     | `20`    | Max results to return (max `100`)      |
| `offset`    | `0`     | Number of results to skip              |

### Get / Update / Delete a single tracked product

```
GET    /trackedProducts/{tracked_product_id}
PATCH  /trackedProducts/{tracked_product_id}
DELETE /trackedProducts/{tracked_product_id}
```

`PATCH` only modifies the fields included in the request body — omitted fields are left untouched.

---

## Roadmap

- [ ] Swap JSON file storage for a real database (Postgres via SQLModel/SQLAlchemy)
- [ ] Add authentication / per-user tracked products (`owner_id` groundwork already present in internal schemas)
- [ ] Add tag endpoints (`/tags`) once tags need to be managed independently of tracked products
- [ ] Background job to poll `current_price` against `target_price` and notify users
- [ ] Test suite (`tests/`)

---

## License

This project was built as part of a personal backend development learning course and is intended for **educational purposes only**. It is not meant for production use as-is. Feel free to read, fork, and adapt the code for your own learning.