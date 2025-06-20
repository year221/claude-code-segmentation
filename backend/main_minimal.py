from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import io
import base64
from PIL import Image
from typing import Optional
import requests

app = FastAPI(title="Semantic Segmentation API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Semantic Segmentation API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Handle image file upload"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # For testing, return the original image as both original and "segmented"
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "original_image": img_str,
            "segmented_image": img_str,  # Same as original for testing
            "filename": file.filename,
            "message": "Image processed (test mode - no actual segmentation)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/segment-url")
async def segment_from_url(image_url: str):
    """Handle image segmentation from URL"""
    try:
        # Download image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # For testing, return the original image as both original and "segmented"
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "original_image": img_str,
            "segmented_image": img_str,  # Same as original for testing
            "source_url": image_url,
            "message": "Image processed (test mode - no actual segmentation)"
        }
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)