"""
Helper utility functions for SoF Event Extractor
"""

import os
import hashlib
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash of the file
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        return ""

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2h 30m", "45m", "1d 3h")
    """
    if seconds < 0:
        return "0m"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m"

def parse_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse various datetime formats commonly found in maritime documents
    
    Args:
        date_str: Date/time string to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Common datetime formats in maritime documents
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%H:%M",
        "%H.%M"
    ]
    
    # Clean the input string
    cleaned_str = date_str.strip()
    
    # Try each format
    for fmt in formats:
        try:
            parsed_dt = datetime.strptime(cleaned_str, fmt)
            
            # If only time is provided, assume current date
            if fmt in ["%H:%M", "%H.%M"]:
                today = datetime.now().date()
                parsed_dt = datetime.combine(today, parsed_dt.time())
            
            return parsed_dt
        except ValueError:
            continue
    
    # Try parsing with regex for more flexible formats
    try:
        return parse_datetime_with_regex(cleaned_str)
    except:
        logger.warning(f"Could not parse datetime: {date_str}")
        return None

def parse_datetime_with_regex(date_str: str) -> Optional[datetime]:
    """
    Parse datetime using regex patterns for flexible parsing
    
    Args:
        date_str: Date/time string to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    # Pattern for date and time
    pattern = r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\s+(\d{1,2}):(\d{2})'
    match = re.search(pattern, date_str)
    
    if match:
        day, month, year, hour, minute = match.groups()
        
        # Handle 2-digit years
        year = int(year)
        if year < 100:
            year += 2000 if year < 50 else 1900
        
        try:
            return datetime(year, int(month), int(day), int(hour), int(minute))
        except ValueError:
            pass
    
    # Pattern for time only
    time_pattern = r'(\d{1,2}):(\d{2})'
    time_match = re.search(time_pattern, date_str)
    
    if time_match:
        hour, minute = time_match.groups()
        try:
            today = datetime.now().date()
            return datetime.combine(today, datetime.strptime(f"{hour}:{minute}", "%H:%M").time())
        except ValueError:
            pass
    
    return None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename or "unnamed_file"

def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def generate_unique_id() -> str:
    """
    Generate a unique identifier
    
    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())

def parse_duration_string(duration_str: str) -> Optional[int]:
    """
    Parse duration string to seconds
    
    Args:
        duration_str: Duration string (e.g., "2h 30m", "1:30:00", "90m")
        
    Returns:
        Duration in seconds or None if parsing fails
    """
    if not duration_str or not isinstance(duration_str, str):
        return None
    
    duration_str = duration_str.strip().lower()
    total_seconds = 0
    
    # Pattern for "HH:MM:SS" or "HH:MM" format
    time_pattern = r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$'
    time_match = re.match(time_pattern, duration_str)
    
    if time_match:
        hours, minutes, seconds = time_match.groups()
        total_seconds = int(hours) * 3600 + int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        return total_seconds
    
    # Pattern for "2h 30m" or "90m" format
    patterns = [
        (r'(\d+)d', 86400),  # days
        (r'(\d+)h', 3600),   # hours
        (r'(\d+)m', 60),     # minutes
        (r'(\d+)s', 1),      # seconds
    ]
    
    for pattern, multiplier in patterns:
        matches = re.findall(pattern, duration_str)
        for match in matches:
            total_seconds += int(match) * multiplier
    
    return total_seconds if total_seconds > 0 else None

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def extract_vessel_name(text: str) -> Optional[str]:
    """
    Extract vessel name from text using common patterns
    
    Args:
        text: Text to search for vessel name
        
    Returns:
        Extracted vessel name or None if not found
    """
    if not text:
        return None
    
    # Common patterns for vessel names
    patterns = [
        r'(?i)(?:m\.?v\.?|vessel|ship)\s+([A-Z][A-Za-z\s\-\']+)',
        r'(?i)vessel\s+name[:\s]+([A-Z][A-Za-z\s\-\']+)',
        r'(?i)ship[:\s]+([A-Z][A-Za-z\s\-\']+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Clean and return the first match
            vessel_name = matches[0].strip()
            # Remove common suffixes/prefixes
            vessel_name = re.sub(r'\s+(arrived|departed|sailed|anchored).*$', '', vessel_name, flags=re.IGNORECASE)
            if len(vessel_name) > 2:  # Minimum reasonable length
                return vessel_name
    
    return None

def extract_imo_number(text: str) -> Optional[str]:
    """
    Extract IMO number from text
    
    Args:
        text: Text to search for IMO number
        
    Returns:
        Extracted IMO number or None if not found
    """
    if not text:
        return None
    
    # IMO numbers are 7 digits
    pattern = r'(?i)imo[:\s]*(\d{7})'
    match = re.search(pattern, text)
    
    if match:
        return match.group(1)
    
    return None

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\/]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text.strip()

def is_valid_coordinate(lat: float, lon: float) -> bool:
    """
    Validate geographic coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180

def calculate_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in nautical miles using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in nautical miles
    """
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in nautical miles
    r_nm = 3440.065
    
    return c * r_nm

def get_port_info(port_name: str) -> dict:
    """
    Get basic information about a port (simplified version)
    
    Args:
        port_name: Name of the port
        
    Returns:
        Dictionary with port information
    """
    # Simplified port database
    ports = {
        'singapore': {
            'name': 'Port of Singapore',
            'country': 'Singapore',
            'timezone': 'Asia/Singapore',
            'lat': 1.2966, 'lon': 103.8006
        },
        'rotterdam': {
            'name': 'Port of Rotterdam',
            'country': 'Netherlands',
            'timezone': 'Europe/Amsterdam',
            'lat': 51.9225, 'lon': 4.47917
        },
        'shanghai': {
            'name': 'Port of Shanghai',
            'country': 'China',
            'timezone': 'Asia/Shanghai',
            'lat': 31.2304, 'lon': 121.4737
        },
        'dubai': {
            'name': 'Port of Dubai',
            'country': 'UAE',
            'timezone': 'Asia/Dubai',
            'lat': 25.2697, 'lon': 55.3094
        }
    }
    
    port_key = port_name.lower().strip()
    return ports.get(port_key, {
        'name': port_name,
        'country': 'Unknown',
        'timezone': 'UTC',
        'lat': None, 'lon': None
    })

def create_backup_filename(original_filename: str) -> str:
    """
    Create a backup filename with timestamp
    
    Args:
        original_filename: Original filename
        
    Returns:
        Backup filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    return f"{name}_backup_{timestamp}{ext}"

def log_performance(func_name: str, start_time: datetime, end_time: datetime, 
                   additional_info: dict = None):
    """
    Log performance metrics for a function
    
    Args:
        func_name: Name of the function
        start_time: Function start time
        end_time: Function end time
        additional_info: Additional information to log
    """
    duration = (end_time - start_time).total_seconds()
    
    log_data = {
        'function': func_name,
        'duration_seconds': duration,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }
    
    if additional_info:
        log_data.update(additional_info)
    
    logger.info(f"Performance: {func_name} completed in {duration:.2f}s", extra=log_data)
