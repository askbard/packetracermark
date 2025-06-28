"""
Development configuration for Packet Tracer Mark Scanner
Use this configuration for development and testing

Version: 0.1
"""

from scripts.config import Config

class DevelopmentConfig(Config):
    """Development configuration with debug settings and faster processing"""
    
    # Debug logging
    LOG_LEVEL = "DEBUG"
    
    # Faster timing for development
    LAUNCH_WAIT_TIME = 10  # Shorter wait for PT launch
    WINDOW_WAIT_TIME = 30  # Shorter window wait
    CAPTURE_DELAY = 0.1    # Faster capture
    
    # Development directories
    IMAGE_DIRECTORY = "dev_images"
    LOG_DIRECTORY = "dev_logs"
    
    # Relaxed consensus for testing
    CONSENSUS_MIN_RESULTS = 2  # Lower requirement for testing
    CONSENSUS_TOLERANCE = 3    # Higher tolerance for development
    
    # Custom Tesseract path for development environment
    # Uncomment and modify if needed
    # TESSERACT_CMD = r'C:\Dev\Tesseract\tesseract.exe'
    
    # Custom PT path for development
    # Uncomment and modify if needed
    # PACKET_TRACER_PATHS = [
    #     r"C:\Dev\PacketTracer\PacketTracer.exe",
    #     *Config.PACKET_TRACER_PATHS  # Include default paths as fallback
    # ]

# To use this configuration, set environment variable:
# set PKA_ENV=development
# or modify the get_config() function in config.py
