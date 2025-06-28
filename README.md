# Packet Tracer Mark Scanner

**Version: 0.1**

A comprehensive toolkit for automating Cisco Packet Tracer (PKA) file processing and mark extraction. This project consists of two main components:

1. **PKA Screenshot Capture Tool** (`pka_capture.py`) - Automatically captures screenshots from PKA instruction windows
2. **OCR Mark Scanner** (`mark_scanner.py`) - Extracts completion percentages from captured screenshots using advanced OCR techniques

## Features

### PKA Screenshot Capture Tool (`pka_capture.py`)
- **Automated PKA Processing**: Automatically opens PKA files and captures instruction windows
- **Advanced Window Management**: Precisely positions and captures PT Activity windows
- **Multiple Capture Methods**: Uses various capture techniques for optimal results
- **Batch Processing**: Processes multiple PKA files in sequence
- **Quality Assurance**: Validates capture quality before saving

### OCR Mark Scanner (`mark_scanner.py`)
- **Advanced OCR Processing**: Uses multiple PSM (Page Segmentation Mode) configurations
- **Consensus Validation**: Requires agreement from multiple OCR attempts for accuracy
- **Multiple Preprocessing**: Applies various image enhancement techniques
- **Individual Scanning**: Interactive scanning for specific student IDs
- **Batch Scanning**: Automatically scan all students at once
- **Results Export**: Save results to CSV files with timestamps
- **Comprehensive Logging**: Detailed logs for debugging and verification
- **Flexible Pattern Matching**: Recognizes various completion percentage formats

## Requirements

### System Requirements
- Windows 10/11 (required for Windows API integration)
- **Screen Resolution**: 1920x1080 (recommended for optimal capture results)
- Cisco Packet Tracer 8.x installed
- Tesseract OCR installed

### Python Dependencies
```
opencv-python>=4.5.0
pytesseract>=0.3.8
Pillow>=8.0.0
pywin32>=227
numpy>=1.20.0
```

## Installation

### 1. Install Tesseract OCR
Download and install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki

**Important**: Install to the default path `C:\Program Files\Tesseract-OCR\` or update the path in the scripts.

### 2. Install Python Dependencies
```bash
pip install opencv-python pytesseract Pillow pywin32 numpy
```

### 3. Download the Scripts
Clone this repository or download the project files. The main launcher and Python scripts are organized as follows:
- `run.py` - **Main launcher with interactive menu (v0.1)** ⭐ **Recommended**
- `scripts/pka_capture.py` - PKA screenshot capture tool (v0.1)
- `scripts/mark_scanner.py` - OCR mark scanner (v0.1)
- `scripts/validate_setup.py` - Setup validation tool (v0.1)
- `scripts/batch_process.py` - Automated batch processing (v0.1)
- `scripts/config.py` - Configuration management (v0.1)

## Quick Start

### Easy Launcher (Recommended)
Use the main launcher for an interactive menu to access all tools:
```bash
python run.py
```

**Expected Output**: Interactive menu with all available options:
```
============================================================
PACKET TRACER MARK SCANNER
============================================================
Choose an option:

1. Validate Setup
2. Capture PKA Screenshots
3. Scan Marks (Individual or All Students)
4. Batch Process (Capture + Scan)
5. Exit

Enter your choice (1-5):
```

### Validate Your Setup
Before using the tools, validate your installation:
```bash
python scripts/validate_setup.py
```

### Automated Batch Processing
For the complete workflow (capture + scan):
```bash
python scripts/batch_process.py
```

**Expected Output**: The batch processor will show real-time progress and comprehensive results:
```
=======================================================================
PACKET TRACER MARK SCANNER - BATCH PROCESSOR
=======================================================================
This script will:
1. 📸 Capture screenshots from PKA files in pka/ directory
2. 🔍 Extract completion marks from captured images using OCR
3. 📊 Generate a comprehensive summary report
4. 💾 Save results to CSV file with timestamp

✅ All prerequisites satisfied
📊 Processed 15 student(s)
📁 Screenshots saved in: images/
📋 Results saved in: results/ directory (CSV format)
📝 Detailed logs saved in: logs/

🎉 BATCH PROCESSING COMPLETED SUCCESSFULLY!
```

## Usage

### PKA Screenshot Capture

1. **Prepare PKA Files**: Place your `.pka` files in the `pka/` directory

2. **Run the Capture Tool**:
```bash
python scripts/pka_capture.py
```

3. **Output**: Screenshots will be saved in the `images/` directory with names matching the PKA files

**Example**:
```
project/
├── scripts/
│   ├── pka_capture.py
│   └── mark_scanner.py
├── pka/
│   ├── student1.pka
│   └── student2.pka
└── images/
    ├── student1.jpg
    └── student2.jpg
```

### OCR Mark Scanning

1. **Prepare Images**: Ensure captured screenshots are in the `images/` directory with naming format: `{StudentID}.jpg`
   - Example: `24075450.jpg`, `24075461.jpg`, etc.
   - One image per student containing the completion percentage

2. **Run the Scanner**:
```bash
python scripts/mark_scanner.py
```

3. **Choose Scanning Mode**:
   - **Individual Mode**: Enter student ID numbers one by one
   - **Batch Mode**: Scan all students at once

4. **Individual Mode Example**:
```
🔍 Enter ID Number: 24075450
```

5. **Batch Mode**: Automatically finds and scans all student IDs
```
📁 Found images for 15 student(s)
🔍 Scan all 15 students? (y/N): y
```

6. **Results**: View extracted marks in comprehensive table format
```
ID Number       Score    Final Marks    Status
--------------------------------------------------
24075450        85       85             ✅ Success
24075461        92       92             ✅ Success
24075462        0        0              ❌ Failed
24075463        78       78             ✅ Success
```

7. **Detailed Results Output**: The scanner provides comprehensive information for each student
```
📊 DETAILED RESULTS TABLE
================================================================================
ID Number    Score    Final Marks    Status
================================================================================
24075450     85       85             ✅ Success (Consensus: 12/35 PSM results)
24075461     92       92             ✅ Success (Consensus: 15/35 PSM results)
24075462     0        0              ❌ Failed (No valid consensus found)
24075463     78       78             ✅ Success (Consensus: 11/35 PSM results)
================================================================================
📈 Summary: 3/4 students processed successfully (75.0% success rate)
📈 Average score: 85.0%
```

8. **CSV Export**: Results are automatically saved to timestamped CSV files
```
📄 Results saved to: results/batch_results_20240628_143022.csv
```

9. **Log Files**: Detailed processing logs are saved for debugging and verification
```
📝 Detailed logs saved in: logs/mark_scanner_20240628_143022.log
📝 Batch processing logs: logs/batch_process_20240628_143022.log
```

## File Naming Convention

For the OCR scanner to work properly, image files must follow this naming pattern:
```
{StudentID}.{extension}
```

**Examples**:
- `24075450.jpg` - Student 24075450
- `24075461.png` - Student 24075461
- `24075462.jpeg` - Student 24075462

**Requirements**:
- One image per student
- Image should contain the completion percentage to be extracted
- Student ID should be alphanumeric (minimum 4 characters)

**Supported Image Formats**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

## Configuration

### Configuration Management
All configuration is centralized in `scripts/config.py`. You can customize:

**Tesseract Path**: Update the `TESSERACT_CMD` variable
```python
TESSERACT_CMD = r'C:\Your\Custom\Path\tesseract.exe'
```

**Packet Tracer Paths**: Add custom paths to `PACKET_TRACER_PATHS` list
```python
PACKET_TRACER_PATHS = [
    r"C:\Your\Custom\Path\PacketTracer.exe",
    # ... existing paths
]
```

**Directory Paths**: Modify directory locations
```python
IMAGE_DIRECTORY = "custom_images"
PKA_DIRECTORY = "custom_pka"
LOG_DIRECTORY = "custom_logs"
```

**Environment Variables**: Set `PKA_ENV=development` for debug mode

## Advanced Features

### OCR Consensus Validation
The mark scanner uses advanced consensus validation:
- **Multiple PSM Modes**: Tests 7 different page segmentation modes
- **Multiple Preprocessing**: Applies 5 different image enhancement techniques
- **Consensus Requirement**: Requires at least 3 similar results (±2% tolerance)
- **Quality Assurance**: Only accepts results with strong agreement

### Logging and Debugging
All tools provide comprehensive logging in the `logs/` directory:
- **Capture Tool**: `logs/pka_capture_{timestamp}.log`
- **Scanner Tool**: `logs/mark_scanner_{timestamp}.log`
- **Batch Processing**: `logs/batch_process_{timestamp}.log`
- **Validation**: Console output with detailed checks

## Troubleshooting

### Common Issues

**1. "Tesseract not found" Error**
```
Solution: Ensure Tesseract is installed and the path is correct in the scripts
```

**2. "No PKA files found" Error**
```
Solution: Place .pka files in the pka/ directory
```

**3. "Packet Tracer not found" Error**
```
Solution: Install Cisco Packet Tracer or update the path in the script
```

**4. Poor OCR Results**
```
Solutions:
- Ensure screenshots are clear and high contrast
- Check that completion percentages are visible in the images
- Review the log files for detailed OCR attempts
```

**5. Window Capture Issues**
```
Solutions:
- Run as administrator for better window access
- Ensure Packet Tracer opens properly
- Check that PT Activity windows are visible
- Use 1920x1080 screen resolution for optimal capture positioning
```

**6. Screenshot Quality Issues**
```
Solutions:
- Set screen resolution to 1920x1080 (recommended)
- Ensure display scaling is set to 100%
- Close other applications to reduce screen clutter
- Check that Packet Tracer windows are not minimized or hidden
```

### Performance Tips

1. **Screen Resolution**: Use 1920x1080 resolution for optimal capture positioning and window management
2. **Display Scaling**: Set Windows display scaling to 100% for accurate coordinate detection
3. **Image Quality**: Higher quality screenshots improve OCR accuracy
4. **System Resources**: Close unnecessary applications during batch processing
5. **File Organization**: Keep PKA files and images organized for easier processing

## Output Examples

### Successful Capture Log
```
2024-01-15 10:30:15 - INFO - Found 3 PKA files
2024-01-15 10:30:16 - INFO - Processing 1/3: student1.pka
2024-01-15 10:30:45 - INFO - SUCCESS: student1.pka (245KB)
```

### Successful OCR Extraction
```
🔍 Processing AT1: 24075450_AT1.jpg
   Testing 7 PSM modes with 5 preprocessing methods...
✅ AT1: 85%
   📊 Consensus from 12 PSM modes (avg: 84.8% → 85%)
```

## Version History

### Version 0.1 (Current)
- Initial release of the Packet Tracer Mark Scanner toolkit
- PKA screenshot capture automation
- Advanced OCR mark extraction with consensus validation
- Batch processing capabilities
- Comprehensive logging and error handling
- Setup validation tools
- Centralized configuration management

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source. Please see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for detailed error information
3. Submit an issue with relevant log excerpts and system information