import torch
import torchvision.transforms as transforms
from torchvision.models.segmentation import deeplabv3_resnet50
import numpy as np
from PIL import Image
import cv2
import logging
import time

class SemanticSegmentationModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Using device: {self.device}")
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load pre-trained DeepLabV3 model"""
        try:
            self.logger.info("Loading pre-trained DeepLabV3 model...")
            start_time = time.time()
            
            # Load pre-trained DeepLabV3 model
            self.model = deeplabv3_resnet50(pretrained=True)
            self.model.eval()
            self.model.to(self.device)
            
            # Define preprocessing transforms
            self.preprocess = transforms.Compose([
                transforms.Resize((520, 520)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            load_time = time.time() - start_time
            self.logger.info(f"Model loaded successfully on {self.device} in {load_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.model = None
    
    def segment_image(self, image: Image.Image) -> Image.Image:
        """
        Perform semantic segmentation on an image
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image object with segmentation overlay
        """
        if self.model is None:
            self.logger.warning("Model not loaded, returning original image")
            return image
            
        try:
            start_time = time.time()
            self.logger.info(f"Starting segmentation for image size: {image.size}")
            
            # Store original size
            original_size = image.size
            
            # Preprocess image
            self.logger.debug("Preprocessing image...")
            input_tensor = self.preprocess(image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            # Perform inference
            self.logger.debug("Performing inference...")
            inference_start = time.time()
            with torch.no_grad():
                output = self.model(input_batch)['out'][0]
            inference_time = time.time() - inference_start
            self.logger.info(f"Inference completed in {inference_time:.3f}s")
                
            # Get predicted class for each pixel
            self.logger.debug("Processing predictions...")
            output_predictions = output.argmax(0).cpu().numpy()
            unique_classes = np.unique(output_predictions)
            self.logger.info(f"Detected classes: {unique_classes.tolist()}")
            
            # Create colored segmentation mask
            segmentation_mask = self.create_colored_mask(output_predictions)
            
            # Resize back to original size
            self.logger.debug(f"Resizing mask from {segmentation_mask.shape} to {original_size}")
            segmentation_mask = cv2.resize(segmentation_mask, original_size)
            
            # Ensure both images have same number of channels
            original_array = np.array(image)
            if len(original_array.shape) == 2:  # Grayscale
                original_array = cv2.cvtColor(original_array, cv2.COLOR_GRAY2RGB)
            elif original_array.shape[2] == 4:  # RGBA
                original_array = cv2.cvtColor(original_array, cv2.COLOR_RGBA2RGB)
            
            # Ensure segmentation mask is 3-channel
            if len(segmentation_mask.shape) == 2:
                segmentation_mask = cv2.cvtColor(segmentation_mask, cv2.COLOR_GRAY2RGB)
            
            # Create overlay (blend original image with segmentation mask)
            alpha = 0.6  # Transparency factor
            overlay = cv2.addWeighted(original_array.astype(np.uint8), alpha, 
                                    segmentation_mask.astype(np.uint8), 1-alpha, 0)
            
            # Convert back to PIL Image
            result_image = Image.fromarray(overlay)
            
            total_time = time.time() - start_time
            self.logger.info(f"Segmentation completed successfully in {total_time:.3f}s total")
            
            return result_image
            
        except Exception as e:
            self.logger.error(f"Error during segmentation: {e}")
            self.logger.error(f"Segmentation error traceback:", exc_info=True)
            # Return original image on error instead of causing server crash
            return image
    
    def create_colored_mask(self, predictions):
        """
        Create a colored segmentation mask from predictions
        
        Args:
            predictions: numpy array of predicted class indices
            
        Returns:
            numpy array representing colored segmentation mask
        """
        # Define colors for different classes (PASCAL VOC classes)
        colors = [
            [0, 0, 0],       # background
            [128, 0, 0],     # aeroplane
            [0, 128, 0],     # bicycle
            [128, 128, 0],   # bird
            [0, 0, 128],     # boat
            [128, 0, 128],   # bottle
            [0, 128, 128],   # bus
            [128, 128, 128], # car
            [64, 0, 0],      # cat
            [192, 0, 0],     # chair
            [64, 128, 0],    # cow
            [192, 128, 0],   # dining table
            [64, 0, 128],    # dog
            [192, 0, 128],   # horse
            [64, 128, 128],  # motorbike
            [192, 128, 128], # person
            [0, 64, 0],      # potted plant
            [128, 64, 0],    # sheep
            [0, 192, 0],     # sofa
            [128, 192, 0],   # train
            [0, 64, 128],    # tv/monitor
        ]
        
        # Extend colors if needed
        while len(colors) <= predictions.max():
            colors.append([np.random.randint(0, 255) for _ in range(3)])
        
        # Create colored mask
        h, w = predictions.shape
        colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        for class_id in range(len(colors)):
            mask = predictions == class_id
            colored_mask[mask] = colors[class_id]
            
        return colored_mask

# Global model instance - with safe initialization
try:
    segmentation_model = SemanticSegmentationModel()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize segmentation model: {e}")
    segmentation_model = None