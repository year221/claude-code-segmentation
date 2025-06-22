from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import io
import base64
from PIL import Image
import numpy as np
from typing import Optional
import requests
import logging
import os
import sys
import traceback
from datetime import datetime
import time
# Try to import segmentation model, fallback to None if dependencies not available
try:
    from models.segmentation import segmentation_model
    SEGMENTATION_AVAILABLE = True
except ImportError:
    segmentation_model = None
    SEGMENTATION_AVAILABLE = False

# Configure logging - stdout/stderr only
class StdoutFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING

class StderrFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.WARNING

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create handlers
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
#stdout_handler.addFilter(StdoutFilter())
stdout_handler.setFormatter(formatter)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
#stderr_handler.addFilter(StderrFilter())
stderr_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[stdout_handler, stderr_handler]
)

logger = logging.getLogger(__name__)

logger.info(f"segmentation {SEGMENTATION_AVAILABLE}")
app = FastAPI(title="Semantic Segmentation API")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {str(e)} - {process_time:.3f}s")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Enable CORS for frontend communication
# Configure CORS origins based on environment
def get_cors_origins():
    # Default origins for development and production
    origins = [
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Alternative React dev server
        "http://localhost",         # Production nginx (default port 80)
        "http://localhost:80",      # Production nginx (explicit port)
        "http://localhost:8000",   
    ]
    
    # Add custom origins from environment variable
    custom_origins = os.getenv("CORS_ORIGINS", "")
    if custom_origins:
        origins.extend(custom_origins.split(","))
    
    logger.info(f"CORS origins configured: {origins}")
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    return {
        "message": "Semantic Segmentation API",
        "timestamp": datetime.now().isoformat(),
        "segmentation_available": SEGMENTATION_AVAILABLE
    }

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Handle image file upload"""
    logger.info(f"Upload request received - filename: {file.filename}, content_type: {file.content_type}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        contents = await file.read()
        logger.info(f"File read successfully - size: {len(contents)} bytes")
        
        image = Image.open(io.BytesIO(contents))
        logger.info(f"Image opened - size: {image.size}, mode: {image.mode}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            logger.info(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Perform semantic segmentation if available, otherwise return original
        if SEGMENTATION_AVAILABLE and segmentation_model:
            logger.info("Starting semantic segmentation")
            try:
                segmented_image = segmentation_model.segment_image(image)
                #segmented_image = image
                logger.info("Segmentation completed successfully")
            except Exception as e:
                logger.error(f"Segmentation failed: {e}")
                logger.error(f"Fallback to original image")
                segmented_image = image  # Fallback to original image
        else:
            logger.warning("Segmentation model not available, returning original image")
            segmented_image = image  # Fallback to original image
        
        # Convert original image to base64
        logger.info("Converting images to base64")
        original_buffered = io.BytesIO()
        image.save(original_buffered, format="PNG")
        original_img_str = base64.b64encode(original_buffered.getvalue()).decode()
        
        # Convert segmented image to base64
        segmented_buffered = io.BytesIO()
        segmented_image.save(segmented_buffered, format="PNG")
        segmented_img_str = base64.b64encode(segmented_buffered.getvalue()).decode()
        
        logger.info(f"Upload processed successfully - original: {len(original_img_str)} chars, segmented: {len(segmented_img_str)} chars")
        
        return {
            "original_image": original_img_str,
            "segmented_image": segmented_img_str,
            "filename": file.filename,
            "processing_info": {
                "segmentation_available": SEGMENTATION_AVAILABLE,
                "image_size": image.size,
                "file_size_bytes": len(contents)
            }
        }
    
    except HTTPException as e:
        logger.error(f"{e}")
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded image: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/segment-url")
async def segment_from_url(image_url: str):
    """Handle image segmentation from URL"""
    logger.info(f"URL segmentation request received - URL: {image_url}")
    
    try:
        # Validate URL format
        if not image_url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL format: {image_url}")
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Download image from URL
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=10, headers={
            'User-Agent': 'Semantic-Segmentation-App/1.0'
        })
        response.raise_for_status()
        
        logger.info(f"Image downloaded successfully - size: {len(response.content)} bytes, content-type: {response.headers.get('content-type')}")
        
        # Validate content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"URL does not point to an image - content-type: {content_type}")
            raise HTTPException(status_code=400, detail="URL does not point to an image")
        
        image = Image.open(io.BytesIO(response.content))
        logger.info(f"Image opened from URL - size: {image.size}, mode: {image.mode}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            logger.info(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Perform semantic segmentation if available, otherwise return original
        if SEGMENTATION_AVAILABLE and segmentation_model:
            logger.info("Starting semantic segmentation on URL image")
            try:
                segmented_image = segmentation_model.segment_image(image)
                logger.info("Segmentation completed successfully")
            except Exception as e:
                logger.error(f"Segmentation failed: {e}")
                logger.error(f"Fallback to original image")
                segmented_image = image  # Fallback to original image
        else:
            logger.warning("Segmentation model not available, returning original image")
            segmented_image = image  # Fallback to original image
        
        # Convert original image to base64
        logger.info("Converting images to base64")
        original_buffered = io.BytesIO()
        image.save(original_buffered, format="PNG")
        original_img_str = base64.b64encode(original_buffered.getvalue()).decode()
        
        # Convert segmented image to base64
        segmented_buffered = io.BytesIO()
        segmented_image.save(segmented_buffered, format="PNG")
        segmented_img_str = base64.b64encode(segmented_buffered.getvalue()).decode()
        
        logger.info(f"URL processing completed successfully - original: {len(original_img_str)} chars, segmented: {len(segmented_img_str)} chars")
        
        return {
            "original_image": original_img_str,
            "segmented_image": segmented_img_str,
            "source_url": image_url,
            "processing_info": {
                "segmentation_available": SEGMENTATION_AVAILABLE,
                "image_size": image.size,
                "downloaded_size_bytes": len(response.content),
                "content_type": content_type
            }
        }
    
    except HTTPException:
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout downloading image from URL: {image_url} - {str(e)}")
        raise HTTPException(status_code=400, detail="Timeout downloading image from URL")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image from URL: {image_url} - {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error downloading image: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing image from URL: {image_url} - {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("=== Semantic Segmentation API Starting ===")
    logger.info(f"Segmentation model available: {SEGMENTATION_AVAILABLE}")
    logger.info("API endpoints configured:")
    logger.info("  GET  / - Health check")
    logger.info("  POST /upload - Image file upload")
    logger.info("  POST /segment-url - Process image from URL")
    logger.info("=== Startup Complete ===")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== Semantic Segmentation API Shutting Down ===")

if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")