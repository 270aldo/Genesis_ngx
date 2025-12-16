"""Genesis NGX Gateway - FastAPI entry point for mobile and web clients.

This gateway serves as the BFF (Backend for Frontend) connecting:
- Expo mobile app (iOS/Android)
- Next.js web app

To the Genesis NGX multi-agent system via Vertex AI Agent Engine.

Usage:
    # Development
    uvicorn gateway.main:app --reload --port 8080

    # Production (Cloud Run)
    uvicorn gateway.main:app --host 0.0.0.0 --port $PORT --workers 2
"""

__version__ = "1.0.0"
