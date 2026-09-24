# Phase 4 Inspection & Architecture

This document describes the design decisions and implementation details for Phase 4: Database, Auth, and User History.

## 1. Database Architecture
The backend uses **SQLAlchemy** connected to **PostgreSQL**.
We chose PostgreSQL because it supports `JSONB` native columns, which allows us to effortlessly store the rich arrays and objects returned by the Phase 2 analysis engine (e.g. `predictions`, `symptom_severity`, `urgency`) without needing to create complex relational tables for every single nested object.

## 2. Models
The database consists of three core models:
1. **User**: Handles authentication (`email`, `hashed_password`).
2. **Analysis**: Represents a snapshot of the deterministic Phase 2 pipeline (`/api/predict` or `/api/analyze`).
3. **Conversation** & **ConversationMessage**: Stores the LLM-driven chat history from `/api/chat`.

## 3. Security and Data Isolation
- Passwords are securely hashed using **bcrypt**.
- Endpoints are secured using **JWT Tokens** (`Bearer`).
- **Strict Data Isolation**: The `get_current_user` dependency automatically resolves the `user_id` from the JWT token.
- Every single GET/DELETE operation in `history.py` and `conversations.py` strictly filters by `user_id == current_user.id`. The frontend cannot spoof the `user_id`.

## 4. Backwards Compatibility
Phase 4 was introduced as an *optional* wrapper. The endpoints `/api/predict`, `/api/analyze`, and `/api/chat` still function flawlessly without an authentication token (anonymous users). 
If a user is authenticated (token is present), the system simply captures the analysis output and persists it to the database for historical tracking. This ensured 0 regressions for the 43 existing tests from Phases 1-3.

## 5. Migrations
We introduced **Alembic** for schema migrations. The initial migration handles table creation and relationships correctly.
