# Examples and Usage Guide

**Version: 0.1**

This directory contains example files and step-by-step guides for using the Packet Tracer Mark Scanner.

## Directory Structure

```
examples/
├── README.md                    # This file
├── config_examples/             # Configuration examples
│   ├── config_development.py    # Development configuration
│   └── config_custom.py         # Custom configuration template
├── sample_data/                 # Sample files for testing
│   ├── pka/                     # Sample PKA files
│   └── images/                  # Sample screenshot images
├── scripts/                     # Utility scripts
│   ├── batch_process.py         # Batch processing script
│   └── validate_setup.py        # Setup validation script
└── tutorials/                   # Step-by-step tutorials
    ├── 01_installation.md       # Installation guide
    ├── 02_basic_usage.md         # Basic usage tutorial
    └── 03_advanced_features.md   # Advanced features guide
```

## Quick Start

1. **Use the Main Launcher (Recommended)**:
   ```bash
   python run.py
   ```

2. **Validate Your Setup**:
   ```bash
   python scripts/validate_setup.py
   ```

3. **Test with Sample Data**:
   ```bash
   # Copy sample PKA files to pka directory
   cp examples/sample_data/pka/*.pka pka/

   # Run batch processing
   python scripts/batch_process.py

   # Or run individual tools
   python scripts/pka_capture.py
   python scripts/mark_scanner.py
   ```

4. **Process Your Own Files**:
   - Place your PKA files in the `pka/` directory
   - Run the capture tool to generate screenshots in `images/`
   - Use the scanner to extract marks and save results to `results/`

## Configuration Examples

See `config_examples/` for different configuration setups:
- Development configuration with debug logging
- Custom paths for different Tesseract/PT installations
- Performance-optimized settings

## Troubleshooting

If you encounter issues:
1. Run the validation script to check your setup
2. Check the log files in the `logs/` directory
3. Review the troubleshooting section in the main README
4. Refer to the tutorials for step-by-step guidance
