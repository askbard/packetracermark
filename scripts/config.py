"""
Configuration module for Packet Tracer Mark Scanner
Centralizes all configurable settings and paths

Version: 0.1
"""

import os
import sys
from pathlib import Path

class Config:
    """Configuration class for the Packet Tracer Mark Scanner"""
    
    # Tesseract OCR Configuration
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Packet Tracer Installation Paths (in order of preference)
    PACKET_TRACER_PATHS = [
        r"C:\Program Files\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe",
        r"C:\Program Files\Cisco Packet Tracer 8.2.1\bin\PacketTracer.exe",
        r"C:\Program Files\Cisco Packet Tracer 8.2.0\bin\PacketTracer.exe", 
        r"C:\Program Files\Cisco Packet Tracer 8.1.1\bin\PacketTracer.exe",
        r"C:\Program Files (x86)\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe",
        r"C:\Program Files (x86)\Cisco Packet Tracer 8.2.1\bin\PacketTracer.exe",
        r"C:\Program Files (x86)\Cisco Packet Tracer 8.1.1\bin\PacketTracer.exe"
    ]
    
    # Directory Configuration (relative to project root, not scripts folder)
    @classmethod
    def get_project_root(cls):
        """Get the project root directory (parent of scripts folder)"""
        return Path(__file__).parent.parent
    
    @property
    def IMAGE_DIRECTORY(self):
        return str(self.get_project_root() / "images")
    
    @property 
    def PKA_DIRECTORY(self):
        return str(self.get_project_root() / "pka")
    
    @property
    def LOG_DIRECTORY(self):
        return str(self.get_project_root() / "logs")
    
    # OCR Configuration
    OCR_PSM_CONFIGS = [
        ("PSM 3", "--psm 3"),   # Fully automatic page segmentation
        ("PSM 6", "--psm 6"),   # Uniform block of text
        ("PSM 7", "--psm 7"),   # Single text line
        ("PSM 8", "--psm 8"),   # Single word
        ("PSM 11", "--psm 11"), # Sparse text
        ("PSM 12", "--psm 12"), # Sparse text with OSD
        ("PSM 13", "--psm 13")  # Raw line
    ]
    
    # Consensus validation settings
    CONSENSUS_MIN_RESULTS = 3
    CONSENSUS_TOLERANCE = 2  # ±2% tolerance for grouping results
    
    # Supported file formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    SUPPORTED_PKA_FORMATS = ['.pka']
    
    # Attempt types for mark scanning
    ATTEMPT_TYPES = ['AT1', 'AT2', 'AT3', 'AT4', 'AT5', 'R1']
    
    # Capture configuration
    CAPTURE_ZONE = {
        'x': 50,
        'y': 50,
        'width': 800,
        'height': 600
    }
    
    # Timing configuration (in seconds)
    LAUNCH_WAIT_TIME = 15
    WINDOW_WAIT_TIME = 60
    WINDOW_WAIT_INTERVAL = 2
    CAPTURE_DELAY = 0.3
    CLEANUP_DELAY = 2
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    @classmethod
    def find_tesseract(cls):
        """Find Tesseract OCR installation"""
        if os.path.exists(cls.TESSERACT_CMD):
            return cls.TESSERACT_CMD
        
        # Try common alternative paths
        alternative_paths = [
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe",
            "tesseract"  # Try system PATH
        ]
        
        for path in alternative_paths:
            if os.path.exists(path) or path == "tesseract":
                return path
        
        return None
    
    @classmethod
    def find_packet_tracer(cls):
        """Find Cisco Packet Tracer installation"""
        for path in cls.PACKET_TRACER_PATHS:
            if os.path.exists(path):
                return path
        return None
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.IMAGE_DIRECTORY, self.LOG_DIRECTORY]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_environment(cls):
        """Validate that all required components are available"""
        issues = []
        
        # Check Tesseract
        tesseract_path = cls.find_tesseract()
        if not tesseract_path:
            issues.append("Tesseract OCR not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
        
        # Check Packet Tracer
        pt_path = cls.find_packet_tracer()
        if not pt_path:
            issues.append("Cisco Packet Tracer not found. Please install Packet Tracer 8.x")
        
        # Check Python version
        if sys.version_info < (3, 7):
            issues.append(f"Python 3.7+ required. Current version: {sys.version}")
        
        return issues
    
    def get_log_filename(self, tool_name):
        """Generate log filename with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.LOG_DIRECTORY, f"{tool_name}_{timestamp}.log")

# Environment-specific configuration
class DevelopmentConfig(Config):
    """Development configuration with debug settings"""
    LOG_LEVEL = "DEBUG"
    LAUNCH_WAIT_TIME = 10  # Shorter wait times for development

class ProductionConfig(Config):
    """Production configuration with optimized settings"""
    LOG_LEVEL = "INFO"
    LAUNCH_WAIT_TIME = 20  # Longer wait times for stability

# Default configuration
DEFAULT_CONFIG = Config

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('PKA_ENV', 'production').lower()
    
    if env == 'development':
        return DevelopmentConfig()
    else:
        return ProductionConfig()
