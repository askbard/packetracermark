#!/usr/bin/env python3
"""
Packet Tracer Mark Scanner - Main Launcher
Provides a simple interface to run all tools

Version: 0.1
"""

import sys
import subprocess
from pathlib import Path

def print_menu():
    """Print the main menu"""
    print("=" * 60)
    print("PACKET TRACER MARK SCANNER")
    print("=" * 60)
    print("Choose an option:")
    print()
    print("1. Validate Setup")
    print("2. Capture PKA Screenshots")
    print("3. Scan Marks (Individual or All Students)")
    print("4. Batch Process (Capture + Scan)")
    print("5. Exit")
    print()

def run_script(script_name):
    """Run a script from the scripts directory"""
    scripts_dir = Path(__file__).parent / "scripts"
    script_path = scripts_dir / script_name
    
    if not script_path.exists():
        print(f"❌ Error: {script_name} not found in scripts directory")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
        return False

def main():
    """Main launcher function"""
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n🔍 Running setup validation...")
                run_script("validate_setup.py")
                
            elif choice == "2":
                print("\n📸 Running PKA capture tool...")
                run_script("pka_capture.py")
                
            elif choice == "3":
                print("\n🔍 Running mark scanner (with individual and batch options)...")
                run_script("mark_scanner.py")
                
            elif choice == "4":
                print("\n🚀 Running batch processor...")
                run_script("batch_process.py")
                
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                continue
                
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
