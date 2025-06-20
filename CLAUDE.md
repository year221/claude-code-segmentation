# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web-based semantic image segmentation application with React frontend and Python FastAPI backend. Users can upload images or provide URLs to get AI-powered semantic segmentation results.

## Architecture

- **Frontend**: React with TypeScript (Vite)
  - Components: ImageUploader, URLInput, ImageDisplay
  - Services: API client with axios
  - Styling: Custom CSS with responsive design

- **Backend**: Python FastAPI
  - REST API endpoints for image processing
  - DeepLabV3 ResNet50 model for semantic segmentation
  - CORS enabled for frontend communication

## Development Commands

### Local Development

#### Backend
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run backend server
python run_backend.py
# Backend runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

#### Frontend
```bash
# Install Node.js dependencies
cd frontend && npm install

# Run frontend development server
./run_frontend.sh
# Frontend runs on http://localhost:5173
```

### Docker Development

#### Production Build
```bash
# Build and run the entire application
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

#### Development Mode
```bash
# Run with hot reload enabled
docker-compose -f docker-compose.dev.yml up --build

# Access frontend at http://localhost:5173
# Access backend at http://localhost:8000
```

#### Docker Commands
```bash
# Build individual services
docker-compose build backend
docker-compose build frontend

# Restart specific service
docker-compose restart backend

# View service logs
docker-compose logs backend
docker-compose logs frontend

# Clean up containers and volumes
docker-compose down -v
docker system prune -f
```

## API Endpoints

- `POST /upload` - Upload image file for segmentation
- `POST /segment-url?image_url=<url>` - Process image from URL
- `GET /` - API health check

## Key Files

- `backend/main.py` - FastAPI application entry point
- `backend/models/segmentation.py` - DeepLabV3 model implementation
- `frontend/src/App.tsx` - Main React component
- `frontend/src/components/` - React UI components
- `frontend/src/services/api.ts` - API client

## Model Information

Uses pre-trained DeepLabV3 with ResNet50 backbone for semantic segmentation. Supports 21 PASCAL VOC classes including person, car, dog, cat, etc. Results are displayed as colored overlay on original image.

## Architecture Documentation

Comprehensive C4 model diagrams and system architecture documentation available in:
- `docs/architecture.md` - Complete system architecture with Mermaid C4 diagrams
- Includes system context, container, component, and deployment diagrams
- Documents data flow, technology stack, and security considerations

## Docker Configuration

### Services

- **Backend**: Python FastAPI application running on port 8000
- **Frontend**: React application served by Nginx on port 80 (production) or 5173 (development)

### Production Deployment

1. **Build and run**: `docker-compose up -d --build`
2. **Access application**: http://localhost (frontend) and http://localhost:8000 (backend API)
3. **Health checks**: Both services include health monitoring
4. **Nginx proxy**: Frontend proxies API requests to backend at `/api/`

### Environment Configuration

Copy `.env.example` to `.env` and customize as needed:
```bash
cp .env.example .env
```

### Troubleshooting

- **Backend health check fails**: Ensure model downloads complete (may take time on first run)
- **Frontend can't reach backend**: Check network connectivity between containers
- **Out of memory**: DeepLabV3 model requires ~2GB RAM minimum

## Logging Configuration

The backend uses structured logging with the following setup:
- **INFO level and above**: Logged to stdout
- **WARNING and ERROR level**: Logged to stderr
- **No file logging**: All logs go to standard streams for container-friendly logging
- **Detailed format**: Timestamp, logger name, level, and message
- **Performance tracking**: Request/response times and processing metrics

To view logs in Docker:
```bash
# View all logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend

# View only error logs (stderr)
docker-compose logs backend 2>&1 | grep -E "(WARNING|ERROR)"
```