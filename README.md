# Database Layer – Migration Notes

This document describes the database layer after the migration from raw SQLite usage to SQLAlchemy ORM.

## Overview

The application now uses **SQLAlchemy ORM** as the primary data access layer. Direct use of `sqlite3` and handwritten SQL has been replaced with:

- SQLAlchemy models in `app/models/`
- Repository classes in `app/db/repositories/`
- Services in `app/services/` that operate on ORM entities
- FastAPI dependency injection for database sessions

The default database backend is still SQLite, but it is now configured via SQLAlchemy.

## Key Components

### Models

Located in `app/models/`:

- `User`
- `Tag`
- `TrackedProduct`
- Association model between tags and tracked products

These are standard SQLAlchemy ORM models, defining tables, columns, and relationships.

### Repositories

Located in `app/db/repositories/`.

Example: `TagRepository`

- Accepts a SQLAlchemy `Session` instance
- Provides methods such as:
  - `save`
  - `save_many`
  - `get_by_id`
  - `get_by_name`
  - `list_all(offset, limit)`
- Handles database errors (`IntegrityError`, `OperationalError`, etc.) and performs session rollbacks on failures.

Repositories return ORM objects (e.g., `Tag`) instead of raw rows or dictionaries. Error paths typically return `None` or an empty list, depending on the method.

### Services

Located in `app/services/`.

Services encapsulate business logic and use repositories internally. They:

- Accept a repository (or repositories) as dependencies
- Convert ORM entities to Pydantic schemas in `app/schemas/` for API responses
- Perform validation and higher-level operations (e.g., attach tags to tracked products)

### API Routers

Located in `app/routers/`.

Routers now:

- Are mostly asynchronous (`async def` handlers)
- Depend on services constructed via FastAPI dependencies
- Do not interact directly with SQLAlchemy sessions or repositories

## Session Management

Database configuration and session management live in `app/db/`.

- A central SQLAlchemy engine and session factory are defined.
- A FastAPI dependency yields a session per request.
- Repositories are constructed with the injected session.

This pattern ensures:

- One session per request (or per unit of work)
- Proper closing/rollback of sessions
- Clear separation between API, services, and data access

## Error Handling

Repositories are responsible for catching database-level exceptions such as:

- `IntegrityError`
- `OperationalError`
- `PendingRollbackError`
- `StatementError`

On failure, repositories:

- Roll back the session to keep it in a valid state
- Log the error with context
- Return `None` or an empty list, depending on the method’s contract

Services and routers can then translate these results into appropriate HTTP responses.

## Type Hints and Return Types

Repositories use precise type hints for better static checking. For example, `TagRepository.list_all` returns a `Sequence[Tag]` and always returns a collection of `Tag` objects (an empty list on error), avoiding unions like `Sequence[Tag] | list[Any]` that complicate callers.

## Upgrading or Adding Features

When adding new database-backed features:

1. **Define or extend a model** in `app/models/`.
2. **Add a repository** in `app/db/repositories/` for all data access.
3. **Add or extend a service** in `app/services/` to hold business logic.
4. **Wire the service into a router** in `app/routers/` using FastAPI dependencies.
5. **Use Pydantic schemas** in `app/schemas/` to define request/response models.

This keeps the architecture consistent and maintains a clear separation of concerns.

## Python and Dependencies

- Minimum Python version: **3.12**
- ORM and DB dependencies:
  - `SQLAlchemy`
  - SQLite as default database backend

Linting and static analysis are configured so that FastAPI dependency helpers are treated as immutable, improving bug detection.

---

For more details, inspect the code under:

- `app/models/`
- `app/db/repositories/`
- `app/services/`
- `app/routers/`

and follow the patterns used for tags and tracked products.
