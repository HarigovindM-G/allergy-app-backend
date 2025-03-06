import logging
import cv2
import numpy as np
import pytesseract
import re
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Annotated, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def correct_orientation(image: np.ndarray) -> np.ndarray:
    """Detect and correct text orientation"""
    try:
        osd = pytesseract.image_to_osd(image)
        angle = int(re.search(r'Rotate: (\d+)', osd).group(1))
        if angle != 0:
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    except Exception as e:
        logger.warning(f"Orientation detection failed: {str(e)}")
    return image

def enhance_image(image: np.ndarray) -> np.ndarray:
    """Enhance image resolution if needed"""
    h, w = image.shape[:2]
    min_dim = 1800  # Minimum dimension for good OCR results
    
    if max(h, w) < min_dim:
        scale_factor = min_dim / max(h, w)
        return cv2.resize(image, None, fx=scale_factor, fy=scale_factor, 
                          interpolation=cv2.INTER_CUBIC)
    return image

def create_processed_variants(image: np.ndarray) -> List[np.ndarray]:
    """Create multiple processed versions of the image for best OCR results"""
    variants = []
    
    # Convert to grayscale
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Add original grayscale
    variants.append(gray)
    
    # Add denoised version
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, searchWindowSize=21, templateWindowSize=7)
    variants.append(denoised)
    
    # Add sharpened version
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    variants.append(sharpened)
    
    # Add binary versions with different thresholds
    # 1. Otsu threshold
    _, otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    
    # 2. Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    variants.append(adaptive)
    
    # 3. Inverted version of thresholds to handle white-on-black text
    variants.append(cv2.bitwise_not(otsu))
    variants.append(cv2.bitwise_not(adaptive))
    
    return variants

def clean_text(text: str) -> str:
    """Clean and normalize OCR output text"""
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text).strip()
    
    # Fix common OCR errors
    cleaned = re.sub(r'l\b', 'i', cleaned)  # Fix 'l' at end of words to 'i'
    cleaned = re.sub(r'O', '0', cleaned)    # Fix 'O' to '0' in numbers
    cleaned = re.sub(r'(\d),(\d)', r'\1.\2', cleaned)  # Fix comma to decimal in numbers
    
    # Fix spacing around punctuation
    cleaned = re.sub(r'\s+([,.;:)])', r'\1', cleaned)
    cleaned = re.sub(r'([([])\s+', r'\1', cleaned)
    
    # Fix sentence boundaries
    cleaned = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', cleaned)
    
    return cleaned

@router.post("/ocr")
async def high_quality_ocr(
    file: Annotated[UploadFile, File()],
    dpi: int = 300,
    language: str = "eng",
    psm: Optional[int] = None
):
    """
    High-reliability OCR endpoint that returns clean text for further processing
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
        
        # Step 1: Correct orientation
        corrected = correct_orientation(image)
        
        # Step 2: Enhance resolution
        enhanced = enhance_image(corrected)
        
        # Step 3: Create multiple processing variants
        variants = create_processed_variants(enhanced)
        
        # Auto-select PSM if not provided
        if psm is None:
            h, w = enhanced.shape[:2]
            if max(h, w) > 1200:  # Larger images likely have multiple text blocks
                psm = 3  # Multiple columns/paragraphs
            elif h < 200 or w / h > 5:  # Very narrow image likely a single line
                psm = 7  # Single text line
            else:
                psm = 11  # Sparse text
        
        # Set up Tesseract config with properly escaped whitelist
        custom_config = (
            f"--dpi {dpi} "
            f"--psm {psm} "
            "--oem 3 "
            f"-l {language} "
            "-c tessedit_char_whitelist=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.,;:/%'\\\"!?()[]{}@#$^&*_+=<>|° \""
        )
        
        # Try all variants and collect results
        all_texts = []
        for variant in variants:
            text = pytesseract.image_to_string(variant, config=custom_config).strip()
            if text:
                all_texts.append(text)
        
        # If no text was found in any variant
        if not all_texts:
            return {"text": "", "success": False, "message": "No text detected in image"}
        
        # Get the longest text (usually the most complete)
        longest_text = max(all_texts, key=len)
        
        # Clean up the text
        cleaned_text = clean_text(longest_text)
        
        # Check if the text is substantially different from other variants
        # If so, use a voting mechanism to get the most likely correct text
        if len(all_texts) > 1:
            words = {}
            for text in all_texts:
                for word in re.findall(r'\b\w+\b', text.lower()):
                    if len(word) > 2:  # Only count words with 3+ characters
                        words[word] = words.get(word, 0) + 1
            
            # If the longest text is missing many common words, combine texts
            common_words = {word for word, count in words.items() if count > 1}
            longest_words = set(re.findall(r'\b\w+\b', longest_text.lower()))
            
            if len(common_words) > 0 and len(common_words - longest_words) > len(common_words) * 0.3:
                # Combine all texts and clean
                combined_text = ' '.join(all_texts)
                cleaned_text = clean_text(combined_text)
        
        return {"text": cleaned_text, "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Processing error: {str(e)}")