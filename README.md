# CamFindAI

**Multi-camera person tracking and re-identification — built for real security operations.**

[![React](https://img.shields.io/badge/React_18-blue?style=flat-square&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=flat-square&logo=apachekafka)](https://kafka.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_15-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

---

CamFindAI ingests multiple live camera feeds and answers one hard question in real time: *is this the same person we saw in camera 3, now appearing in camera 7?*

It does this using deep metric learning — each detected person is encoded into a 512-dimensional embedding, and those embeddings are matched across camera views using cosine similarity. The result: a unified identity timeline across your entire facility, streamed live to a secure web dashboard.

Built with airports, corporate campuses, and smart city deployments in mind.

---

## How It Works

The system has three layers that talk to each other asynchronously.

### 1. AI Pipeline (Multi-Camera Worker)

YOLOv8 handles person detection; OSNet generates re-identification embeddings. Each camera feed runs in its own background thread so one slow stream never stalls the others. A dynamic quality engine monitors system FPS and adjusts WebSocket JPEG compression (70% → 30%) under load to keep playback smooth. Embeddings are pushed to Apache Kafka the moment they're produced.

### 2. Event-Driven Backend (FastAPI + Kafka)

Three Kafka consumers run independently:

- **Matching Engine** — compares incoming embeddings against all active tracks using cosine similarity and assigns a consistent Global ID across cameras
- **Rules Engine** — cross-references identity matches against predefined spatial zones and fires alerts (e.g., "Restricted Zone Breach")
- **Persistence** — asynchronously writes all trajectory points and alerts to PostgreSQL for forensic auditing

Live video frames and alerts stream to connected clients over WebSockets.

### 3. Frontend (React + Vite)

A dark-themed, real-time dashboard that renders bounding boxes and Global ID tags directly on live video. Operators can define spatial zones, review alerts, and pull up any identity's complete movement history across the facility.

---

## Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| Frontend | React 18, TypeScript, Tailwind CSS v4 | Real-time operations dashboard |
| Backend API | FastAPI, Uvicorn | REST endpoints + WebSocket streaming |
| Database | PostgreSQL, Alembic | Users, orgs, alerts, trajectories |
| Message Broker | Apache Kafka | High-throughput embedding & event bus |
| AI / ML | PyTorch, YOLOv8, OSNet | Detection, tracking, feature extraction |

---

## Getting Started

**Prerequisites:** Python 3.9+, Node.js 18+, Docker

### 1. Clone and install

```bash
# Backend
cd CamFindAI
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd camfindai-ui
npm install
```

### 2. Start infrastructure

```bash
docker-compose up -d   # PostgreSQL, Kafka, Zookeeper
```

### 3. Initialize the database

```bash
# From the root directory
source venv/bin/activate
python -m alembic upgrade head

# Optional: seed with mock cameras and zones
python scripts/seed_db.py
```

### 4. Run the full stack

**Terminal 1 — Backend, workers, and Kafka consumers:**

```bash
source venv/bin/activate
./start.sh
```

**Terminal 2 — Frontend:**

```bash
cd camfindai-ui
npm run dev
```

Open `http://localhost:5173/register` to create your workspace and add your first camera.

---

## Authentication

The platform uses organization-based multi-tenancy.

- **Registration** — creating a workspace at `/register` provisions an `Organization` and an `Admin` user in PostgreSQL
- **Auth** — all API endpoints and WebSocket connections are secured with JWT

---

## Screenshots

**Login**
![Login page](https://github.com/user-attachments/assets/009b7fa1-2cff-4119-b114-4352a867bd07)

**Register**
![Register page](https://github.com/user-attachments/assets/3ab86ba5-951c-4a91-bb75-98da613c935d)

**Live View**
![Live view](https://github.com/user-attachments/assets/eb4adee4-2671-40e8-8255-a50186de6b33)

**Cameras**
![Cameras](https://github.com/user-attachments/assets/aec858a7-957c-406c-8f57-638f0513d986)

**Identities**
![Identities](https://github.com/user-attachments/assets/1063bd39-7511-4ed4-90c7-b02c4651ff82)

**Timeline**
![Timeline](https://github.com/user-attachments/assets/37c4cab0-97fb-4d16-953d-8efa9090546c)

**Alerts**
![Alerts](https://github.com/user-attachments/assets/90c4419b-51af-4a4e-8512-3e89a391d951)

**Settings**
![Settings](https://github.com/user-attachments/assets/9e3da5fc-e559-430d-9ebe-91a2ea2a3a5b)

---

## What I'd Build Next

- **`pgvector` / Milvus** — replace in-memory cosine similarity with a vector DB so matching scales to millions of stored identities without degrading
- **WebRTC** — transition live video from WebSocket binary streams to WebRTC for sub-100ms latency and lower bandwidth
- **Kubernetes** — containerize camera workers and scale out processing nodes dynamically
- **Analytics endpoints** — surface heatmaps and historical tracking paths from the existing `trajectory_points` table
- **SSO** — wire up the OAuth2 buttons on the registration page to Azure AD, Okta, and Google Workspace
