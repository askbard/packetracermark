#!/usr/bin/env python3
"""
Setup Validation Script for Packet Tracer Mark Scanner
Checks if all required components are properly installed and configured

Version: 0.1
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the scripts directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_config

config = get_config()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 7):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (Compatible)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.7+)")
        return False

def check_required_modules():
    """Check if all required Python modules are installed"""
    print("\n📦 Checking required Python modules...")
    
    required_modules = [
        ('cv2', 'opencv-python'),
        ('pytesseract', 'pytesseract'),
        ('PIL', 'Pillow'),
        ('win32gui', 'pywin32'),
        ('numpy', 'numpy')
    ]
    
    all_good = True
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (Not installed)")
            all_good = False
    
    return all_good

def check_tesseract():
    """Check if Tesseract OCR is installed and accessible"""
    print("\n🔍 Checking Tesseract OCR...")
    
    # Use config to find Tesseract
    tesseract_path = config.find_tesseract()
    
    if tesseract_path:
        try:
            if tesseract_path == "tesseract":
                result = subprocess.run(['tesseract', '--version'], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run([tesseract_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"   ✅ Tesseract found: {version_line}")
                if tesseract_path != "tesseract":
                    print(f"      Path: {tesseract_path}")
                return True
        except subprocess.TimeoutExpired:
            pass
    
    print("   ❌ Tesseract OCR not found")
    print("      Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def check_packet_tracer():
    """Check if Cisco Packet Tracer is installed"""
    print("\n🌐 Checking Cisco Packet Tracer...")
    
    pt_path = config.find_packet_tracer()
    
    if pt_path:
        print(f"   ✅ Packet Tracer found at: {pt_path}")
        return True
    else:
        print("   ❌ Cisco Packet Tracer not found")
        print("      Please install Packet Tracer 8.x from Cisco Networking Academy")
        return False

def check_directories():
    """Check if required directories exist or can be created"""
    print("\n📁 Checking directory structure...")
    
    project_root = config.get_project_root()
    required_dirs = [
        ('pka', config.PKA_DIRECTORY),
        ('images', config.IMAGE_DIRECTORY), 
        ('logs', config.LOG_DIRECTORY)
    ]
    
    all_good = True
    for dir_name, dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_name}/ directory exists")
        else:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   ✅ {dir_name}/ directory created")
            except Exception as e:
                print(f"   ❌ Cannot create {dir_name}/ directory: {e}")
                all_good = False
    
    return all_good

def check_sample_files():
    """Check for sample PKA files"""
    print("\n📄 Checking for PKA files...")
    
    pka_dir = Path(config.PKA_DIRECTORY)
    
    if pka_dir.exists():
        pka_files = list(pka_dir.glob('*.pka'))
        if pka_files:
            print(f"   ✅ Found {len(pka_files)} PKA file(s):")
            for pka_file in pka_files[:5]:  # Show first 5 files
                print(f"      - {pka_file.name}")
            if len(pka_files) > 5:
                print(f"      ... and {len(pka_files) - 5} more")
            return True
        else:
            print("   ⚠️  No PKA files found in pka/ directory")
            print("      Place your .pka files in the pka/ directory to test")
            return False
    else:
        print("   ❌ pka/ directory not found")
        return False

def check_scripts():
    """Check if all required scripts are present"""
    print("\n📜 Checking for required scripts...")
    
    scripts_dir = Path(__file__).parent
    required_scripts = [
        'config.py',
        'pka_capture.py', 
        'mark_scanner.py'
    ]
    
    all_good = True
    for script_name in required_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            print(f"   ✅ {script_name}")
        else:
            print(f"   ❌ {script_name} (Missing)")
            all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("=" * 60)
    print("PACKET TRACER MARK SCANNER - SETUP VALIDATION")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Modules", check_required_modules),
        ("Required Scripts", check_scripts),
        ("Tesseract OCR", check_tesseract),
        ("Packet Tracer", check_packet_tracer),
        ("Directories", check_directories),
        ("PKA Files", check_sample_files)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to use the Packet Tracer Mark Scanner.")
        print("\nNext steps:")
        print("1. Place PKA files in the pka/ directory")
        print("2. Run: python scripts/pka_capture.py")
        print("3. Run: python scripts/mark_scanner.py")
    else:
        print(f"\n⚠️  {total - passed} issue(s) found. Please address the failed checks above.")
        print("Refer to the README.md for installation instructions.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
