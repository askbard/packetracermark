#!/usr/bin/env python3
"""
Batch Processing Script for Packet Tracer Mark Scanner
Automates the complete workflow: capture screenshots and extract marks

Version: 0.1
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import logging

# Add the scripts directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_config

config = get_config()

# Setup logging
config.create_directories()
log_filename = config.get_log_filename('batch_process')
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_capture_tool():
    """Run the PKA capture tool"""
    print("\n" + "="*60)
    print("STEP 1: CAPTURING PKA SCREENSHOTS")
    print("="*60)
    
    try:
        # Check if capture script exists
        scripts_dir = Path(__file__).parent
        capture_script = scripts_dir / 'pka_capture.py'
        
        if not capture_script.exists():
            print("❌ Error: pka_capture.py not found in scripts directory")
            return False
        
        # Run the capture tool
        print("🚀 Starting PKA capture process...")
        print("📸 This will automatically open PKA files and capture screenshots...")
        print("⏳ Please wait while processing...")

        # Run with real-time output
        process = subprocess.Popen([sys.executable, str(capture_script)],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 text=True,
                                 universal_newlines=True)

        # Show real-time output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")

        return_code = process.poll()

        if return_code == 0:
            print("\n✅ PKA capture completed successfully")
            logging.info("PKA capture completed successfully")
            return True
        else:
            print(f"\n❌ PKA capture failed with exit code {return_code}")
            logging.error(f"PKA capture failed with exit code {return_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error running capture tool: {e}")
        logging.error(f"Error running capture tool: {e}")
        return False

def get_student_ids_from_images():
    """Extract student IDs from image filenames"""
    images_dir = Path(config.IMAGE_DIRECTORY)
    if not images_dir.exists():
        return []

    student_ids = set()
    # Check for all supported image formats
    for ext in config.SUPPORTED_IMAGE_FORMATS:
        pattern = f"*{ext}"
        for image_file in images_dir.glob(pattern):
            # Extract ID from filename pattern: ID.extension
            student_id = image_file.stem
            # Validate that this looks like a student ID (basic check)
            if student_id.isdigit() or (student_id.isalnum() and len(student_id) >= 4):
                student_ids.add(student_id)

    return sorted(list(student_ids))

def run_scanner_for_ids(student_ids):
    """Run the OCR scanner for specific student IDs"""
    print("\n" + "="*60)
    print("STEP 2: EXTRACTING MARKS WITH OCR")
    print("="*60)
    
    if not student_ids:
        print("❌ No student IDs found in images")
        return False
    
    try:
        # Check if scanner script exists
        scripts_dir = Path(__file__).parent
        scanner_script = scripts_dir / 'mark_scanner.py'
        
        if not scanner_script.exists():
            print("❌ Error: mark_scanner.py not found in scripts directory")
            return False
        
        print(f"📊 Found {len(student_ids)} student ID(s): {', '.join(student_ids[:5])}")
        if len(student_ids) > 5:
            print(f"    ... and {len(student_ids) - 5} more")
        
        # Import the scanner module to use its functions
        sys.path.insert(0, str(scripts_dir))
        from mark_scanner import scan_id_manual, setup_logging, print_all_results_table
        
        # Setup logging for the scanner
        setup_logging()
        
        # Process each student ID
        all_results = []
        successful_scans = 0

        print(f"\n🚀 Starting batch scan of {len(student_ids)} students...")
        print(f"🔍 Using consensus validation (requires ≥{config.CONSENSUS_MIN_RESULTS} similar PSM results)")

        for i, student_id in enumerate(student_ids, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING {i}/{len(student_ids)}: {student_id}")
            print(f"{'='*60}")

            # Scan this student ID with detailed logging
            student_data = scan_id_manual(student_id)

            if student_data and student_data['Score'] >= 0:
                all_results.append(student_data)
                successful_scans += 1

                # Show brief summary for batch mode
                score = student_data['Score']
                status = "✅ Success" if score > 0 else "⚠️ No score detected"
                print(f"\n📊 Result for {student_id}: {score}% - {status}")
            else:
                print(f"\n❌ Failed to process student {student_id}: No image found or processing failed")

        # Display comprehensive results table
        if all_results:
            print_all_results_table(all_results)

        # Save results to file
        save_batch_results(all_results)

        # Final summary
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"📊 Total students: {len(student_ids)}")
        print(f"✅ Successfully processed: {successful_scans}")
        print(f"❌ Failed: {len(student_ids) - successful_scans}")

        if successful_scans > 0:
            avg_score = sum(r['Score'] for r in all_results if r['Score'] > 0) / max(successful_scans, 1)
            print(f"📈 Average score: {avg_score:.1f}%")

        return True
        
    except Exception as e:
        print(f"❌ Error running scanner: {e}")
        logging.error(f"Error running scanner: {e}")
        return False

def save_batch_results(results):
    """Save batch processing results to a CSV file"""
    if not results:
        return
    
    try:
        import csv
        from datetime import datetime
        
        # Create results directory if it doesn't exist
        results_dir = config.get_project_root() / "results"
        results_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = results_dir / f"batch_results_{timestamp}.csv"
        
        # Write CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID Number', 'Score', 'Final Marks']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"📄 Results saved to: {csv_filename}")
        logging.info(f"Batch results saved to: {csv_filename}")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not save results to CSV: {e}")
        logging.warning(f"Could not save results to CSV: {e}")

def check_prerequisites():
    """Check if all required files and directories exist"""
    print("🔍 Checking prerequisites...")
    
    issues = []
    
    # Check for required scripts
    scripts_dir = Path(__file__).parent
    required_files = ['config.py', 'pka_capture.py', 'mark_scanner.py']
    for file_name in required_files:
        file_path = scripts_dir / file_name
        if not file_path.exists():
            issues.append(f"Missing required script: {file_name}")
    
    # Check for PKA directory
    pka_dir = Path(config.PKA_DIRECTORY)
    if not pka_dir.exists():
        issues.append(f"PKA directory '{config.PKA_DIRECTORY}' not found")
    else:
        pka_files = list(pka_dir.glob('*.pka'))
        if not pka_files:
            issues.append(f"No PKA files found in '{config.PKA_DIRECTORY}' directory")
        else:
            print(f"   ✅ Found {len(pka_files)} PKA file(s)")
    
    # Check/create images directory
    images_dir = Path(config.IMAGE_DIRECTORY)
    if not images_dir.exists():
        try:
            images_dir.mkdir(parents=True)
            print(f"   ✅ Created '{config.IMAGE_DIRECTORY}' directory")
        except Exception as e:
            issues.append(f"Cannot create '{config.IMAGE_DIRECTORY}' directory: {e}")
    else:
        print(f"   ✅ Images directory exists")
    
    if issues:
        print("❌ Prerequisites check failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ All prerequisites satisfied")
        return True

def main():
    """Main batch processing function"""
    print("=" * 70)
    print("PACKET TRACER MARK SCANNER - BATCH PROCESSOR")
    print("=" * 70)
    print("This script will:")
    print("1. 📸 Capture screenshots from PKA files in pka/ directory")
    print("2. 🔍 Extract completion marks from captured images using OCR")
    print("3. 📊 Generate a comprehensive summary report")
    print("4. 💾 Save results to CSV file with timestamp")
    print("-" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Cannot proceed due to missing prerequisites")
        return False
    
    # Step 1: Capture screenshots
    if not run_capture_tool():
        print("\n❌ Batch processing failed at capture stage")
        return False
    
    # Wait a moment for file system to settle
    time.sleep(2)
    
    # Step 2: Extract student IDs from captured images
    student_ids = get_student_ids_from_images()
    
    # Step 3: Run OCR scanner
    if not run_scanner_for_ids(student_ids):
        print("\n❌ Batch processing failed at scanning stage")
        return False
    
    # Summary
    print("\n" + "="*70)
    print("🎉 BATCH PROCESSING COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("✅ All steps completed successfully")
    print(f"📊 Processed {len(student_ids)} student(s)")
    print(f"📁 Screenshots saved in: {config.IMAGE_DIRECTORY}/")
    print("📋 Results saved in: results/ directory (CSV format)")
    print(f"📝 Detailed logs saved in: {config.LOG_DIRECTORY}/")
    print("\n🔍 Next steps:")
    print("   • Review the results CSV file for all student scores")
    print("   • Check log files if any students failed processing")
    print("   • Individual images can be re-processed using option 3 if needed")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Batch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error in batch processing: {e}")
        sys.exit(1)
