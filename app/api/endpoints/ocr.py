import logging
import cv2
import numpy as np
import pytesseract
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Annotated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def smart_preprocessing(image: np.ndarray) -> np.ndarray:
    """Adaptive preprocessing based on image characteristics with improved inversion and noise reduction"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate image metrics
    brightness = np.mean(gray)
    contrast = np.std(gray)
    
    # Apply processing based on image quality
    if contrast < 40:  # Low contrast image
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        processed = clahe.apply(gray)
    else:
        processed = gray.copy()
    
    # Apply thresholding
    if brightness > 200 and contrast > 80:  # Likely clean digital text
        _, thresh = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:  # For scanned docs/photos
        thresh = cv2.adaptiveThreshold(
            processed, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
    
    # Improved inversion detection based on majority pixel value
    num_white = cv2.countNonZero(thresh)  # Count white pixels (255)
    if num_white <= (thresh.size / 2):    # If white pixels are minority, invert
        thresh = cv2.bitwise_not(thresh)
    
    # Noise reduction with median blur
    thresh = cv2.medianBlur(thresh, 3)
    
    return thresh

@router.post("/ocr")
async def enhanced_ocr_v2(
    file: Annotated[UploadFile, File()],
    dpi: int = 300,
    psm: int = 3
):
    """
    Improved OCR with adaptive preprocessing and configurable parameters
    """
    try:
        # Validate input
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "Invalid file type")
        
        contents = await file.read()
        if not contents:
            raise HTTPException(400, "Empty file received")

        # Decode image
        np_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(400, "Invalid image format")

        # Adaptive preprocessing
        processed_image = smart_preprocessing(image)

        # Configure Tesseract
        custom_config = (
            f'--dpi {dpi} '
            f'--psm {psm} '
            '--oem 3 '
            '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.,:;/\\!?()[]{}@#$%^&*_+=<> '
            '-l eng'
        )

        # Perform OCR
        text = pytesseract.image_to_string(
            processed_image,
            config=custom_config
        )

        # Post-processing
        cleaned = ' '.join(text.strip().split())
        
        return {"text": cleaned}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Processing error: {str(e)}")