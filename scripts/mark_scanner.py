"""
Manual Mode PKA Mark Scanner
Allows user to enter ID number and scans all IDNumber* files using multiple PSM values
Shows marks in format: ID Number  AT1  AT2  AT3  AT4  AT5  R1  Final Marks

Version: 0.1
"""

import os
import cv2
import pytesseract
import re
import logging
from pathlib import Path
from config import get_config

# Get configuration
config = get_config()

# Configure Tesseract path
tesseract_path = config.find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("Warning: Tesseract OCR not found. Please install Tesseract.")
    print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")

def setup_logging():
    """Setup logging configuration"""
    config.create_directories()
    log_filename = config.get_log_filename('mark_scanner')
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return log_filename

def extract_completion_percentage_multi_psm(image_path):
    """Extract completion percentage using multiple PSM modes with consensus validation"""
    try:
        logging.info(f"Processing image: {os.path.basename(image_path)}")

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            logging.error(f"Could not read image: {image_path}")
            return 0, "Image read failed"

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Multiple preprocessing methods
        preprocessing_methods = [
            ("Original", lambda img: cv2.convertScaleAbs(img, alpha=1.2, beta=10)),
            ("CLAHE", lambda img: cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(img)),
            ("High Contrast", lambda img: cv2.convertScaleAbs(img, alpha=2.0, beta=30)),
            ("Enhanced CLAHE", lambda img: cv2.createCLAHE(clipLimit=5.0, tileGridSize=(16,16)).apply(img)),
            ("Bilateral+OTSU", lambda img: cv2.threshold(cv2.bilateralFilter(img, 9, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
        ]

        # Use configured PSM configurations for consensus validation
        psm_configs = config.OCR_PSM_CONFIGS

        # Store all results for consensus analysis
        all_psm_results = []

        # Try each preprocessing method with each PSM config
        for method_name, preprocess_func in preprocessing_methods:
            try:
                processed_img = preprocess_func(gray)

                # Test all PSM modes with this preprocessing
                psm_results = []

                for psm_name, psm_config in psm_configs:
                    try:
                        # Extract text using current config
                        text = pytesseract.image_to_string(processed_img, config=psm_config)

                        # Comprehensive completion percentage patterns
                        completion_patterns = [
                            r'Completion[:\s]*(\d{1,3})%',        # Completion: XX%
                            r'completion[:\s]*(\d{1,3})%',        # completion: XX%
                            r'(\d{1,3})%\s*[Cc]omplete',         # XX% complete
                            r'(\d{1,3})%\s*[Cc]ompleted',        # XX% completed
                            r'(\d{1,3})%',                       # Any XX%
                            r'Score[:\s]*(\d{1,3})%',            # Score: XX%
                            r'Progress[:\s]*(\d{1,3})%',         # Progress: XX%
                        ]

                        found_percentages = []
                        for pattern in completion_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            if matches:
                                for match in matches:
                                    try:
                                        percentage = int(match)
                                        if 0 <= percentage <= 100:
                                            found_percentages.append(percentage)
                                    except ValueError:
                                        continue

                        if found_percentages:
                            max_percentage = max(found_percentages)
                            psm_results.append((psm_name, max_percentage))
                            logging.info(f"PSM {psm_name} with {method_name}: {max_percentage}%")
                        else:
                            psm_results.append((psm_name, 0))

                    except Exception as e:
                        logging.warning(f"PSM config {psm_name} with {method_name} failed: {e}")
                        psm_results.append((psm_name, 0))
                        continue

                # Store results for this preprocessing method
                all_psm_results.append((method_name, psm_results))

            except Exception as e:
                logging.warning(f"Preprocessing method {method_name} failed: {e}")
                continue

        # Analyze consensus across PSM modes
        consensus_result, consensus_info = analyze_psm_consensus(all_psm_results)

        if consensus_result > 0:
            logging.info(f"Consensus result: {consensus_result}% - {consensus_info}")
            return consensus_result, consensus_info
        else:
            logging.warning(f"No consensus found across PSM modes for {image_path}")
            return 0, "No consensus across PSM modes"

    except Exception as e:
        logging.error(f"Error extracting percentage from {image_path}: {e}")
        return 0, f"Error: {str(e)}"

def analyze_psm_consensus(all_psm_results):
    """Analyze PSM results to find consensus (at least 3 similar results)"""
    try:
        # Collect all percentage values from all PSM modes
        all_percentages = []

        for method_name, psm_results in all_psm_results:
            for psm_name, percentage in psm_results:
                if percentage > 0:  # Only consider non-zero results
                    all_percentages.append((percentage, f"{method_name}+{psm_name}"))

        if len(all_percentages) < config.CONSENSUS_MIN_RESULTS:
            return 0, f"Insufficient results ({len(all_percentages)} < {config.CONSENSUS_MIN_RESULTS})"

        # Group similar percentages (within configured tolerance)
        percentage_groups = {}

        for percentage, method_info in all_percentages:
            # Find if this percentage belongs to an existing group
            group_found = False
            for group_key in percentage_groups:
                if abs(percentage - group_key) <= config.CONSENSUS_TOLERANCE:
                    percentage_groups[group_key].append((percentage, method_info))
                    group_found = True
                    break

            if not group_found:
                percentage_groups[percentage] = [(percentage, method_info)]

        # Find groups with at least 3 similar results
        valid_groups = []
        for group_key, group_values in percentage_groups.items():
            if len(group_values) >= config.CONSENSUS_MIN_RESULTS:
                # Calculate average of the group
                avg_percentage = sum(p for p, _ in group_values) / len(group_values)
                valid_groups.append((avg_percentage, len(group_values), group_values))

        if not valid_groups:
            return 0, f"No consensus: largest group has {max(len(v) for v in percentage_groups.values())} results (need ≥{config.CONSENSUS_MIN_RESULTS})"

        # Select the group with highest average percentage
        best_group = max(valid_groups, key=lambda x: x[0])
        avg_percentage, group_size, group_values = best_group

        # Round to nearest integer
        final_percentage = round(avg_percentage)

        # Create consensus info
        methods_used = [method_info for _, method_info in group_values]
        consensus_info = f"Consensus from {group_size} PSM modes (avg: {avg_percentage:.1f}% → {final_percentage}%)"

        logging.info(f"Consensus analysis: {consensus_info}")
        logging.info(f"Methods in consensus: {', '.join(methods_used[:5])}{'...' if len(methods_used) > 5 else ''}")

        return final_percentage, consensus_info

    except Exception as e:
        logging.error(f"Error in consensus analysis: {e}")
        return 0, f"Consensus analysis error: {str(e)}"

def find_images_for_id(id_number, image_directory=None):
    """Find image for a specific ID number"""
    if image_directory is None:
        image_directory = config.IMAGE_DIRECTORY

    found_images = {}

    if not os.path.exists(image_directory):
        print(f"Error: Image directory '{image_directory}' not found!")
        return found_images

    # Look for images with pattern: ID.extension
    image_extensions = config.SUPPORTED_IMAGE_FORMATS

    for ext in image_extensions:
        image_filename = f"{id_number}{ext}"
        image_path = os.path.join(image_directory, image_filename)

        if os.path.exists(image_path):
            found_images['MAIN'] = image_path
            break

    return found_images

def scan_id_manual(id_number, image_directory=None):
    """Scan image for a specific ID number manually with PSM consensus"""
    if image_directory is None:
        image_directory = config.IMAGE_DIRECTORY

    print(f"\n{'='*60}")
    print(f"SCANNING ID: {id_number}")
    print(f"{'='*60}")

    # Find images for this ID
    found_images = find_images_for_id(id_number, image_directory)

    if not found_images:
        print(f"❌ No image found for ID {id_number}")
        return None

    print(f"📁 Found image: {os.path.basename(list(found_images.values())[0])}")
    print(f"🔍 Using consensus validation (requires ≥{config.CONSENSUS_MIN_RESULTS} similar PSM results)")

    # Initialize student record
    student_data = {
        'ID Number': id_number,
        'Score': -1,
        'Final Marks': -1
    }

    # Process the found image
    for attempt, image_path in found_images.items():
        print(f"\n🔍 Processing: {os.path.basename(image_path)}")
        print(f"   Testing {len(config.OCR_PSM_CONFIGS)} PSM modes with 5 preprocessing methods...")

        completion_mark, consensus_info = extract_completion_percentage_multi_psm(image_path)
        student_data['Score'] = completion_mark
        student_data['Final Marks'] = completion_mark

        if completion_mark > 0:
            print(f"✅ Score: {completion_mark}%")
            print(f"   📊 {consensus_info}")
        else:
            print(f"❌ Score: 0%")
            print(f"   ⚠️  {consensus_info}")

    return student_data

def print_results_table(student_data):
    """Print results in table format"""
    if student_data is None:
        return

    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")

    # Header
    print(f"{'ID Number':<15} {'Score':<8} {'Status':<10}")
    print("-" * 50)

    # Data row
    status = "✅ Success" if student_data['Score'] > 0 else "❌ Failed"
    print(f"{student_data['ID Number']:<15} "
          f"{student_data['Score']:<8} "
          f"{status:<10}")

    print("-" * 50)

    # Summary
    print(f"📊 Summary:")
    print(f"   • Student ID: {student_data['ID Number']}")
    print(f"   • Extracted Score: {student_data['Score']}%")
    print(f"   • Status: {'Success' if student_data['Score'] > 0 else 'No score detected'}")

def get_all_student_ids_from_images(image_directory=None):
    """Get all unique student IDs from image files in the directory"""
    if image_directory is None:
        image_directory = config.IMAGE_DIRECTORY

    if not os.path.exists(image_directory):
        return []

    student_ids = set()
    image_extensions = config.SUPPORTED_IMAGE_FORMATS

    # Scan all image files in the directory
    for ext in image_extensions:
        pattern = f"*{ext}"
        for image_file in Path(image_directory).glob(pattern):
            # Extract ID from filename pattern: ID.extension
            student_id = image_file.stem
            # Validate that this looks like a student ID (basic check)
            if student_id.isdigit() or (student_id.isalnum() and len(student_id) >= 4):
                student_ids.add(student_id)

    return sorted(list(student_ids))

def scan_all_students(image_directory=None):
    """Scan all student IDs found in the image directory"""
    if image_directory is None:
        image_directory = config.IMAGE_DIRECTORY

    print(f"\n{'='*60}")
    print("SCANNING ALL STUDENTS")
    print(f"{'='*60}")

    # Get all student IDs
    student_ids = get_all_student_ids_from_images(image_directory)

    if not student_ids:
        print("❌ No student images found in the directory")
        print(f"   Looking for images in: {image_directory}")
        print("   Expected format: StudentID.extension")
        print("   Example: 24075450.jpg")
        return []

    print(f"📁 Found {len(student_ids)} student(s): {', '.join(student_ids[:10])}")
    if len(student_ids) > 10:
        print(f"    ... and {len(student_ids) - 10} more")

    # Ask for confirmation
    confirm = input(f"\n🔍 Scan all {len(student_ids)} students? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Scan cancelled")
        return []

    print(f"\n🚀 Starting batch scan of {len(student_ids)} students...")
    print(f"🔍 Using consensus validation (requires ≥{config.CONSENSUS_MIN_RESULTS} similar PSM results)")

    all_results = []
    successful_scans = 0

    for i, student_id in enumerate(student_ids, 1):
        print(f"\n{'='*40}")
        print(f"Processing {i}/{len(student_ids)}: {student_id}")
        print(f"{'='*40}")

        # Scan this student
        student_data = scan_id_manual(student_id, image_directory)

        if student_data:
            all_results.append(student_data)
            successful_scans += 1

            # Show brief results
            score = student_data['Score']
            print(f"✅ {student_id}: Score: {score}%")
        else:
            print(f"❌ {student_id}: No images found or processing failed")

    # Print summary table
    print_all_results_table(all_results)

    # Save results
    save_results_to_csv(all_results)

    print(f"\n📊 Batch scan completed:")
    print(f"   • Total students: {len(student_ids)}")
    print(f"   • Successfully processed: {successful_scans}")
    print(f"   • Failed: {len(student_ids) - successful_scans}")

    return all_results

def print_all_results_table(results):
    """Print results for all students in a table format"""
    if not results:
        return

    print(f"\n{'='*60}")
    print("ALL STUDENTS RESULTS")
    print(f"{'='*60}")

    # Header
    print(f"{'ID Number':<15} {'Score':<8} {'Status':<12}")
    print("-" * 60)

    # Data rows
    for student_data in results:
        status = "✅ Success" if student_data['Score'] > 0 else "❌ Failed"

        print(f"{student_data['ID Number']:<15} "
              f"{student_data['Score']:<8} "
              f"{status:<12}")

    print("-" * 60)

    # Summary statistics
    total_students = len(results)
    students_with_marks = len([r for r in results if r['Score'] > 0])
    avg_score = sum(r['Score'] for r in results if r['Score'] > 0) / max(students_with_marks, 1)

    print(f"📊 Summary:")
    print(f"   • Total students processed: {total_students}")
    print(f"   • Students with valid scores: {students_with_marks}")
    print(f"   • Average score: {avg_score:.1f}%")

def save_results_to_csv(results):
    """Save results to a CSV file"""
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
        csv_filename = results_dir / f"scan_results_{timestamp}.csv"

        # Write CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID Number', 'Score', 'Final Marks']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in results:
                writer.writerow(result)

        print(f"💾 Results saved to: {csv_filename}")

    except Exception as e:
        print(f"⚠️  Warning: Could not save results to CSV: {e}")
        logging.warning(f"Could not save results to CSV: {e}")

def main():
    """Main function with options for individual or batch scanning"""
    # Setup logging
    setup_logging()

    print("=" * 80)
    print("MARK SCANNER - PKA MARK SCANNER")
    print("=" * 80)
    print("Extract completion marks from PKA screenshot images")
    print(f"🔍 Uses {len(config.OCR_PSM_CONFIGS)} PSM modes with 5 preprocessing methods")
    print(f"✅ Consensus validation: Requires ≥{config.CONSENSUS_MIN_RESULTS} similar results for accuracy")
    print(f"📊 Tolerance: ±{config.CONSENSUS_TOLERANCE}% for grouping similar results")
    print("-" * 80)

    image_directory = config.IMAGE_DIRECTORY

    # Check if image directory exists
    if not os.path.exists(image_directory):
        print(f"❌ Error: Image directory '{image_directory}' not found!")
        print("Please make sure you're running this script from the correct directory.")
        return

    # Check what student IDs are available
    available_ids = get_all_student_ids_from_images(image_directory)

    if not available_ids:
        print(f"❌ No student images found in '{image_directory}' directory")
        print("Expected format: StudentID.extension (e.g., 24075450.jpg)")
        return

    print(f"📁 Found images for {len(available_ids)} student(s)")

    # Show scanning options
    print("\nScanning Options:")
    print("1. Scan individual student (enter ID numbers one by one)")
    print("2. Scan all students at once")
    print("3. Exit")

    while True:
        try:
            choice = input("\nChoose option (1-3): ").strip()

            if choice == "1":
                # Individual scanning mode
                print(f"\n📋 Available student IDs: {', '.join(available_ids[:10])}")
                if len(available_ids) > 10:
                    print(f"    ... and {len(available_ids) - 10} more")
                print("Enter ID numbers to scan (type 'back' to return to menu, 'quit' to exit)")

                while True:
                    try:
                        user_input = input("\n🔍 Enter ID Number: ").strip()

                        if user_input.lower() in ['quit', 'exit', 'q']:
                            print("\n👋 Goodbye!")
                            return
                        elif user_input.lower() in ['back', 'b']:
                            break
                        elif not user_input:
                            print("❌ Please enter a valid ID number")
                            continue

                        # Scan the ID
                        student_data = scan_id_manual(user_input, image_directory)

                        # Print results
                        print_results_table(student_data)

                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted by user. Goodbye!")
                        return
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        continue

            elif choice == "2":
                # Batch scanning mode
                scan_all_students(image_directory)
                break

            elif choice == "3":
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
