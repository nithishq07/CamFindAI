
# CamFindAI 

**Intelligent Multi-Camera Person Tracking & Re-Identification Platform**

CamFindAI is an enterprise-grade surveillance intelligence platform designed for large-scale physical security operations (Airports, Smart Cities, Corporate Campuses). It ingests multiple live video feeds, tracks individuals across non-overlapping camera views using Deep Metric Learning (Re-Identification), and presents real-time actionable intelligence through a secure, high-performance web dashboard.

---

##  System Architecture

The platform is designed around a decoupled, event-driven microservices architecture to ensure high throughput and low latency for real-time video analytics.

### 1. The Core AI Pipeline (Multi-Camera Worker)
- **Technology**: Python, OpenCV, PyTorch, YOLOv8 (Tracking), OSNet (ReID)
- **Function**: A high-performance, threaded worker manager that handles dynamic ingestion of multiple camera streams (Webcams, RTSP, IP).
  - **Zero-Block I/O**: Captures frames in lightweight background threads to ensure the UI streaming never blocks.
  - **Dynamic Video Quality Engine**: Automatically tracks system FPS and adjusts WebSocket JPEG compression (from 70% to 30%) under heavy load to guarantee smooth video playback.
  - **AI Scale-down**: YOLOv8 aggressively downscales input to 640px for near-linear speedups. Tracking relies purely on high-speed spatial IOU matching (bypassing heavy CPU embedders), while 512-dimensional OSNet features are extracted periodically.
- **Data Output**: Pushes embeddings and bounding box metadata directly to Apache Kafka topics.

### 2. Event-Driven Backend (FastAPI + Kafka)
- **Technology**: Python, FastAPI, Apache Kafka, PostgreSQL, SQLAlchemy
- **Function**: The central nervous system of the platform.
  - **Matching Engine Consumer**: Subscribes to the Kafka `reid.embeddings` topic. It compares incoming embeddings against active tracks using Cosine Similarity to assign global identities (Global IDs) across multiple cameras.
  - **Rules Engine Consumer**: Listens for identity matches and cross-references them against predefined spatial zones to trigger security alerts (e.g., "Restricted Zone Breach").
  - **Persistence Consumer**: Asynchronously logs all trajectory points and alerts to PostgreSQL for forensic search and auditing.
  - **Websocket Manager**: Streams live video frames, active alerts, and identity updates directly to the frontend client in real-time.

### 3. Enterprise Frontend (React + Vite)
- **Technology**: React 18, Vite, TypeScript, Tailwind CSS (v4), Lucide Icons
- **Function**: A mission-critical, dark-themed UI inspired by platforms like Palantir and Verkada.
  - Features real-time video rendering via WebSocket binary streams.
  - Renders live bounding boxes and Global ID tags over the video feeds.
  - Provides an organization-level registration and authentication portal with JWT authorization.

---

##  Tech Stack Summary

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript, TailwindCSS | Real-time Operations Dashboard |
| **Backend API** | FastAPI, Uvicorn | REST endpoints, WebSocket streaming |
| **Database** | PostgreSQL, Alembic | Persistent storage (Users, Orgs, Alerts, Trajectories) |
| **Message Broker** | Apache Kafka | High-throughput embedding & event streaming |
| **AI/ML** | PyTorch, YOLO, OSNet | Object Detection, Tracking, and Feature Extraction |

---

##  Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL running locally
- Apache Kafka & Zookeeper running locally (or via Docker Compose)

### 1. Environment Setup
Clone the repository and set up the Python virtual environment:
```bash
cd CamFindAI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up the Frontend:
```bash
cd camfindai-ui
npm install
```

### 2. Database Initialization
Ensure PostgreSQL is running, then run Alembic migrations to build the schema:
```bash
# From the root directory
source venv/bin/activate
python -m alembic upgrade head

# (Optional) Seed the database with mock cameras and zones
python scripts/seed_db.py
```

### 3. Starting the Services
You need two terminal windows to run the full stack locally.

**Terminal 1: Backend, Multi-Camera Worker & Kafka Consumers**
```bash
source venv/bin/activate
./start.sh
```

**Terminal 2: Frontend Server**
```bash
cd camfindai-ui
npm run dev
```

The system will automatically initialize the dynamic Camera Worker manager. You can add, edit, and start cameras directly from the UI Dashboard (Cameras tab)!

---

##  Authentication & Onboarding

The platform utilizes a secure Organization-based tenancy model.
- **Registration**: Operators can create a new Workspace at `http://localhost:5173/register`. This creates an `Organization` and an `Admin User` in the PostgreSQL database.
- **Authentication**: JWT (JSON Web Tokens) are used to secure all API endpoints and WebSocket connections.

---

##  Future Roadmap & Development

For future iterations and team handoffs, consider the following development vectors:

1. **Scalability (Kubernetes)**: Dockerize the Camera Workers, FastAPI backend, and Frontend. Deploy the Kafka cluster and microservices via Kubernetes to scale out camera processing nodes dynamically.
2. **Advanced Analytics**: Implement the `/analytics` endpoints to provide heatmaps and historical tracking paths using the `trajectory_points` table.
3. **WebRTC Integration**: Transition the live video streaming from Base64 WebSockets to WebRTC for sub-100ms latency and drastically reduced bandwidth.
4. **Vector Database**: As the system scales to thousands of identities, replace the in-memory Cosine Similarity search with a dedicated Vector Database (e.g., Milvus, Qdrant, or pgvector) for lightning-fast Re-ID matching.
5. **SSO Integration**: Hook up the mock SSO buttons on the Registration page to actual OAuth2 providers (Azure AD, Okta, Google Workspace).

##  Screenshots of User Interface
1. **Login page**:
  <img width="1470" height="956" alt="Screenshot 2026-06-22 at 9 43 11 PM" src="https://github.com/user-attachments/assets/4c9faba5-b7f4-4191-83c7-8d0054cbceeb" />
2. **Register page**:
  
