import cv2
import numpy as np
import os
from datetime import datetime

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Pytesseract not available - OCR disabled")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def extract_text_from_image(image_path):
    """
    Extract text from image using OCR (Tesseract)
    Returns: dict with extracted text, confidence, and detected languages
    """
    if not PYTESSERACT_AVAILABLE:
        return {
            'text': '',
            'confidence': 0,
            'languages': ['en'],
            'error': 'OCR not available'
        }
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            return {'text': '', 'confidence': 0, 'languages': [], 'error': 'Cannot read image'}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply image preprocessing for better OCR
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        
        # Extract text with config for better detection
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, config=custom_config)
        
        # Get confidence data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Detect languages (basic heuristic based on character patterns)
        languages = detect_language(text)
        
        return {
            'text': text.strip(),
            'confidence': round(avg_confidence, 1),
            'languages': languages,
            'word_count': len(text.split()),
            'has_address': contains_address(text),
            'has_landmark': contains_landmark(text)
        }
    except Exception as e:
        return {'text': '', 'confidence': 0, 'languages': [], 'error': str(e)}


def detect_language(text):
    """
    Simple language detection based on character patterns
    """
    languages = ['en']
    
    if not text:
        return languages
    
    # Check for Hindi/Devanagari characters
    if any('\u0900' <= c <= '\u097F' for c in text):
        languages.append('hi')
    
    # Check for Tamil
    if any('\u0B80' <= c <= '\u0BFF' for c in text):
        languages.append('ta')
    
    # Check for Telugu
    if any('\u0C00' <= c <= '\u0C7F' for c in text):
        languages.append('te')
    
    # Check for Bengali
    if any('\u0980' <= c <= '\u09FF' for c in text):
        languages.append('bn')
    
    return languages


def contains_address(text):
    """
    Heuristic to detect if extracted text contains address-like content
    """
    address_keywords = ['road', 'street', 'lane', 'block', 'sector', 'area', 'nagar', 
                       'colony', 'plot', 'no.', 'near', 'opp', 'opposite']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in address_keywords)


def contains_landmark(text):
    """
    Heuristic to detect if text contains landmarks
    """
    landmarks = ['park', 'school', 'hospital', 'temple', 'church', 'mosque', 
                 'market', 'station', 'bus', 'railway', 'bank', 'atm']
    text_lower = text.lower()
    return any(landmark in text_lower for landmark in landmarks)


def assess_image_quality(image_path):
    """
    Assess if the uploaded image is clear enough for analysis
    Returns: quality score (0-100), issues list, recommendation
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return {'score': 0, 'issues': ['Cannot read image'], 'recommendation': 'Upload a clearer image'}
        
        issues = []
        score = 100
        
        # Check 1: Resolution
        height, width = image.shape[:2]
        total_pixels = height * width
        if total_pixels < 500000:  # Less than 0.5MP
            issues.append('Low resolution')
            score -= 30
        elif total_pixels < 1000000:  # Less than 1MP
            issues.append('Medium resolution')
            score -= 15
        
        # Check 2: Blur detection using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 30:
            issues.append('Image is blurry')
            score -= 25
        elif laplacian_var < 50:
            issues.append('Image could be sharper')
            score -= 10
        
        # Check 3: Brightness
        mean_brightness = np.mean(gray)
        if mean_brightness < 50:
            issues.append('Image is too dark')
            score -= 20
        elif mean_brightness > 220:
            issues.append('Image is too bright')
            score -= 20
        
        # Check 4: Contrast
        contrast = gray.std()
        if contrast < 30:
            issues.append('Low contrast')
            score -= 15
        
        # Check 5: Check if image is mostly uniform (might be blank/empty)
        if contrast < 10:
            issues.append('Image appears blank/empty')
            score -= 40
        
        # Generate recommendation
        if score >= 80:
            recommendation = 'Image is good quality for analysis'
        elif score >= 50:
            recommendation = 'Image is usable but may affect AI accuracy'
        else:
            recommendation = 'Please upload a clearer image for better results'
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendation': recommendation,
            'details': {
                'resolution': f'{width}x{height}',
                'sharpness': round(laplacian_var, 1),
                'brightness': round(mean_brightness, 1),
                'contrast': round(contrast, 1)
            }
        }
    except Exception as e:
        return {'score': 50, 'issues': ['Error analyzing image'], 'recommendation': str(e)}


def compare_before_after(before_path, after_path):
    """
    Compare before and after images to verify issue resolution
    Returns: similarity score, changes detected, verification status
    """
    try:
        before_img = cv2.imread(before_path)
        after_img = cv2.imread(after_path)
        
        if before_img is None or after_img is None:
            return {'error': 'Cannot read one or both images'}
        
        # Resize to same dimensions for comparison
        after_resized = cv2.resize(after_img, (before_img.shape[1], before_img.shape[0]))
        
        # Convert to grayscale
        before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after_resized, cv2.COLOR_BGR2GRAY)
        
        # Calculate structural similarity
        diff = cv2.absdiff(before_gray, after_gray)
        similarity = 100 - (np.mean(diff) / 255 * 100)
        
        # Calculate histogram similarity
        hist_before = cv2.calcHist([before_gray], [0], None, [256], [0, 256])
        hist_after = cv2.calcHist([after_gray], [0], None, [256], [0, 256])
        hist_compare = cv2.compareHist(hist_before, hist_after, cv2.HISTCMP_CORREL)
        
        # Check for significant changes (likely indicates cleanup/repair)
        significant_changes = np.sum(diff > 50) / diff.size * 100
        
        # Determine verification status
        if similarity < 40 and significant_changes > 20:
            status = 'resolved'
            message = 'Significant changes detected - issue appears resolved'
        elif similarity > 80:
            status = 'no_change'
            message = 'Images are very similar - issue may not be resolved'
        else:
            status = 'partial'
            message = 'Some changes detected - partial resolution'
        
        return {
            'similarity_score': round(similarity, 1),
            'change_percentage': round(significant_changes, 1),
            'histogram_similarity': round(hist_compare * 100, 1),
            'status': status,
            'message': message,
            'verified': status in ['resolved', 'partial']
        }
    except Exception as e:
        return {'error': str(e)}


def extract_location_hints(image_path):
    """
    Extract potential location hints from image (signs, landmarks, text)
    """
    result = extract_text_from_image(image_path)
    quality = assess_image_quality(image_path)
    
    hints = []
    confidence = 0
    
    if result.get('text'):
        if result.get('has_address'):
            hints.append('Address text detected')
            confidence += 30
        if result.get('has_landmark'):
            hints.append('Landmark detected')
            confidence += 25
        if result.get('languages') and len(result.get('languages', [])) > 1:
            hints.append(f"Multilingual: {', '.join(result['languages'])}")
    
    if quality['score'] >= 80:
        hints.append('High quality image')
        confidence += 20
    elif quality['score'] < 50:
        hints.append('Low quality - may affect detection')
        confidence -= 10
    
    return {
        'hints': hints,
        'confidence': min(100, max(0, confidence)),
        'extracted_text': result.get('text', '')[:200],
        'quality_score': quality['score']
    }