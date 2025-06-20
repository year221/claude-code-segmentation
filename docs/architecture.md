# Semantic Segmentation Application Architecture

This document provides C4 model diagrams for the web-based semantic segmentation application using Mermaid notation.

## C4 Level 1: System Context Diagram

```mermaid
C4Context
    title System Context diagram for Semantic Segmentation Application
    
    Person(user, "User", "Person who wants to perform semantic segmentation on images")
    
    System(segApp, "Semantic Segmentation Application", "Web-based application that processes images using AI to identify and segment different objects/regions")
    
    System_Ext(imageHost, "External Image Hosts", "Third-party image hosting services (e.g., social media, cloud storage)")
    System_Ext(modelRepo, "Model Repository", "Pre-trained AI models (e.g., HuggingFace, PyTorch Hub)")
    
    Rel(user, segApp, "Uploads images or provides URLs", "HTTPS")
    Rel(segApp, imageHost, "Fetches images from URLs", "HTTPS")
    Rel(segApp, modelRepo, "Downloads pre-trained models", "HTTPS")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## C4 Level 2: Container Diagram

```mermaid
C4Container
    title Container diagram for Semantic Segmentation Application
    
    Person(user, "User", "Person using the web application")
    
    Container_Boundary(segApp, "Semantic Segmentation Application") {
        Container(webapp, "Web Application", "React, TypeScript", "Provides the user interface for image upload and segmentation visualization")
        Container(api, "API Application", "Python, FastAPI", "Handles image processing, AI inference, and serves RESTful API")
        Container(nginx, "Web Server", "Nginx", "Serves static files and proxies API requests")
    }
    
    System_Ext(imageHost, "External Image Hosts", "Third-party image hosting")
    System_Ext(browser, "Web Browser", "User's web browser")
    
    Rel(user, browser, "Uses", "")
    Rel(browser, nginx, "Makes requests", "HTTPS")
    Rel(nginx, webapp, "Serves", "HTTP")
    Rel(nginx, api, "Proxies API calls", "HTTP")
    Rel(webapp, api, "Makes API calls", "HTTPS/HTTP")
    Rel(api, imageHost, "Fetches images", "HTTPS")
    
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## C4 Level 3: Component Diagram - Frontend

```mermaid
C4Component
    title Component diagram for Web Application (Frontend)
    
    Container_Boundary(webapp, "Web Application - React Frontend") {
        Component(app, "App Component", "React Component", "Main application component, manages global state")
        Component(uploader, "Image Uploader", "React Component", "Handles file uploads with drag & drop functionality")
        Component(urlInput, "URL Input", "React Component", "Allows users to input external image URLs")
        Component(display, "Image Display", "React Component", "Shows original and segmented images side-by-side")
        Component(apiService, "API Service", "Axios Client", "Handles HTTP communication with backend API")
        Component(types, "Type Definitions", "TypeScript", "Defines interfaces for API responses and data models")
    }
    
    Container_Ext(api, "API Application", "FastAPI Backend")
    Container_Ext(nginx, "Web Server", "Nginx")
    
    Rel(app, uploader, "Renders", "")
    Rel(app, urlInput, "Renders", "")
    Rel(app, display, "Renders", "")
    Rel(uploader, apiService, "Calls upload API", "")
    Rel(urlInput, apiService, "Calls URL processing API", "")
    Rel(apiService, types, "Uses", "")
    Rel(apiService, api, "Makes HTTP requests", "HTTPS")
    Rel(nginx, webapp, "Serves built assets", "HTTP")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## C4 Level 3: Component Diagram - Backend

```mermaid
C4Component
    title Component diagram for API Application (Backend)
    
    Container_Boundary(api, "API Application - FastAPI Backend") {
        Component(main, "Main Application", "FastAPI", "ASGI application with CORS middleware and route definitions")
        Component(uploadEndpoint, "Upload Endpoint", "FastAPI Route", "Handles multipart file uploads and validation")
        Component(urlEndpoint, "URL Endpoint", "FastAPI Route", "Processes images from external URLs")
        Component(segModel, "Segmentation Model", "PyTorch/DeepLabV3", "AI model for semantic segmentation inference")
        Component(imageProcessor, "Image Processor", "PIL/OpenCV", "Handles image preprocessing and postprocessing")
        Component(validator, "Input Validator", "FastAPI", "Validates file types, sizes, and URL formats")
    }
    
    Container_Ext(webapp, "Web Application", "React Frontend")
    System_Ext(imageHost, "External Image Hosts", "Third-party services")
    System_Ext(modelRepo, "Model Repository", "Pre-trained models")
    
    Rel(webapp, main, "Makes API requests", "HTTPS")
    Rel(main, uploadEndpoint, "Routes /upload", "")
    Rel(main, urlEndpoint, "Routes /segment-url", "")
    Rel(uploadEndpoint, validator, "Validates files", "")
    Rel(urlEndpoint, validator, "Validates URLs", "")
    Rel(uploadEndpoint, imageProcessor, "Processes images", "")
    Rel(urlEndpoint, imageProcessor, "Processes images", "")
    Rel(imageProcessor, segModel, "Performs inference", "")
    Rel(urlEndpoint, imageHost, "Fetches images", "HTTPS")
    Rel(segModel, modelRepo, "Loads models", "HTTPS")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## C4 Level 4: Code Diagram - Segmentation Model

```mermaid
C4Component
    title Code diagram for Segmentation Model Component
    
    Container_Boundary(segModel, "Segmentation Model Component") {
        Component(modelClass, "SemanticSegmentationModel", "Python Class", "Main model wrapper class")
        Component(loader, "Model Loader", "Method", "Loads pre-trained DeepLabV3 model with ResNet50 backbone")
        Component(preprocessor, "Image Preprocessor", "Method", "Resizes, normalizes, and converts images to tensors")
        Component(inference, "Inference Engine", "Method", "Performs forward pass through neural network")
        Component(postprocessor, "Result Postprocessor", "Method", "Converts predictions to colored segmentation masks")
        Component(colorizer, "Mask Colorizer", "Method", "Maps class indices to PASCAL VOC colors")
        Component(blender, "Image Blender", "Method", "Overlays segmentation mask on original image")
    }
    
    System_Ext(torch, "PyTorch", "Deep learning framework")
    System_Ext(torchvision, "TorchVision", "Computer vision models")
    System_Ext(opencv, "OpenCV", "Image processing library")
    
    Rel(modelClass, loader, "Initializes", "")
    Rel(modelClass, preprocessor, "Calls", "")
    Rel(modelClass, inference, "Calls", "")
    Rel(modelClass, postprocessor, "Calls", "")
    Rel(loader, torchvision, "Loads DeepLabV3", "")
    Rel(preprocessor, torch, "Creates tensors", "")
    Rel(inference, torch, "GPU/CPU computation", "")
    Rel(postprocessor, colorizer, "Uses", "")
    Rel(postprocessor, blender, "Uses", "")
    Rel(blender, opencv, "Image operations", "")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Deployment Diagram

```mermaid
C4Deployment
    title Deployment diagram for Semantic Segmentation Application
    
    Deployment_Node(docker, "Docker Environment", "Container Runtime") {
        Deployment_Node(frontend_container, "Frontend Container", "nginx:alpine") {
            Container(nginx_prod, "Nginx", "Web Server", "Serves React app and proxies API calls")
            Container(react_build, "React App", "Static Files", "Production build of frontend application")
        }
        
        Deployment_Node(backend_container, "Backend Container", "python:3.11-slim") {
            Container(fastapi_app, "FastAPI", "ASGI Server", "Python backend with uvicorn")
            Container(ml_models, "AI Models", "PyTorch", "DeepLabV3 segmentation model")
        }
        
        Deployment_Node(network, "Docker Network", "Bridge Network") {
            ContainerDb(bridge, "segmentation-network", "Internal communication")
        }
    }
    
    Deployment_Node(host, "Host Machine", "Docker Host") {
        Deployment_Node(ports, "Port Mapping", "Host Ports") {
            Container(port80, "Port 80", "HTTP", "Frontend access")
            Container(port8000, "Port 8000", "HTTP", "Backend API access")
        }
    }
    
    Person(user, "User", "Application user")
    
    Rel(user, port80, "Accesses web app", "HTTP")
    Rel(user, port8000, "Direct API access", "HTTP")
    Rel(port80, nginx_prod, "Routes to", "")
    Rel(port8000, fastapi_app, "Routes to", "")
    Rel(nginx_prod, fastapi_app, "Proxies /api/*", "HTTP")
    Rel(react_build, nginx_prod, "Served by", "")
    Rel(fastapi_app, ml_models, "Uses", "")
    Rel(frontend_container, bridge, "Connected to", "")
    Rel(backend_container, bridge, "Connected to", "")
    
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Data Flow Diagram

```mermaid
flowchart TD
    A[User uploads image/URL] --> B{Input Type?}
    B -->|File Upload| C[Validate file type & size]
    B -->|URL| D[Fetch image from URL]
    
    C --> E[Convert to PIL Image]
    D --> E
    
    E --> F[Preprocess Image]
    F --> G[Resize to 520x520]
    G --> H[Normalize RGB values]
    H --> I[Convert to PyTorch tensor]
    
    I --> J[Load DeepLabV3 Model]
    J --> K[Perform inference]
    K --> L[Get pixel predictions]
    
    L --> M[Create colored mask]
    M --> N[Map classes to PASCAL VOC colors]
    N --> O[Blend with original image]
    
    O --> P[Convert to base64]
    P --> Q[Return JSON response]
    Q --> R[Display results in UI]
    
    style A fill:#e1f5fe
    style R fill:#e8f5e8
    style J fill:#fff3e0
    style K fill:#fff3e0
```

## Technology Stack Overview

```mermaid
graph TB
    subgraph "Frontend Technologies"
        A[React 19] --> B[TypeScript]
        B --> C[Vite Build Tool]
        C --> D[Axios HTTP Client]
        D --> E[React Dropzone]
    end
    
    subgraph "Backend Technologies"
        F[Python 3.11] --> G[FastAPI]
        G --> H[Uvicorn ASGI]
        H --> I[PyTorch]
        I --> J[TorchVision]
        J --> K[OpenCV]
        K --> L[Pillow]
    end
    
    subgraph "Infrastructure"
        M[Docker] --> N[Docker Compose]
        N --> O[Nginx]
        O --> P[Docker Networks]
    end
    
    subgraph "AI/ML"
        Q[DeepLabV3] --> R[ResNet50 Backbone]
        R --> S[PASCAL VOC Classes]
        S --> T[Semantic Segmentation]
    end
    
    A -.->|API Calls| G
    O -.->|Serves| A
    O -.->|Proxies| G
    I -.->|Loads| Q
```

## Security & Performance Considerations

### Security Features
- CORS middleware for cross-origin requests
- Input validation for file types and URLs
- Nginx security headers (XSS protection, content type sniffing prevention)
- No sensitive data exposure in responses
- Container isolation with Docker networks

### Performance Optimizations
- Multi-stage Docker builds for smaller images
- Asset compression and caching in Nginx
- Model caching to avoid repeated downloads
- Efficient image processing with PIL/OpenCV
- GPU acceleration support for inference (when available)

### Monitoring & Health Checks
- Docker health checks for both containers
- API endpoint health monitoring
- Graceful error handling and fallbacks
- Structured logging for debugging