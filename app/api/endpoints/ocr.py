import logging
import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Annotated

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ocr")
async def perform_ocr(file: Annotated[UploadFile, File()]):
    """
    Detailed OCR processing with extensive logging
    """
    # Log all incoming file details
    logger.debug(f"Received file - Name: {file.filename}, Content-Type: {file.content_type}")

    # Extensive file type validation
    allowed_types = [
        "image/jpeg", 
        "image/png", 
        "image/jpg", 
        "image/gif", 
        "application/octet-stream"
    ]
    
    if not file.content_type or file.content_type not in allowed_types:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types are: {', '.join(allowed_types)}"
        )

    try:
        # Read file contents with logging
        contents = await file.read()
        logger.debug(f"File size: {len(contents)} bytes")

        # Validate file is not empty
        if len(contents) == 0:
            logger.warning("Received empty file")
            raise HTTPException(status_code=400, detail="Empty file received")

        # Convert bytes to a NumPy array for OpenCV
        try:
            np_array = np.frombuffer(contents, np.uint8)
            cv_img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        except Exception as decode_error:
            logger.error(f"Image decoding error: {decode_error}")
            raise HTTPException(status_code=400, detail="Unable to decode image")

        # Validate image was successfully decoded
        if cv_img is None:
            logger.warning("Failed to decode image")
            raise HTTPException(status_code=400, detail="Unable to process image")

        # Preprocessing
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # Convert processed array back to PIL for pytesseract
        pil_img = Image.fromarray(thresh)

        # Run Tesseract
        raw_text = pytesseract.image_to_string(pil_img)

        # Clean text
        cleaned_text = " ".join(raw_text.split())

        logger.info(f"Extracted text: {cleaned_text}")

        return {"text": cleaned_text}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during OCR: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")