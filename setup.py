#!/usr/bin/env python3
"""
Setup script for Flu Vaccination Analysis Dashboard
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "Flu_shot_cleaned.csv",
        "aggregated_data/county_agg.csv",
        "aggregated_data/year_agg.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required data files found!")
        return True

def main():
    print("🚀 Setting up Flu Vaccination Analysis Dashboard")
    print("=" * 50)
    
    # Check data files
    if not check_data_files():
        print("\nPlease ensure all data files are present before running the dashboard.")
        return False
    
    # Install requirements
    if not install_requirements():
        print("\nFailed to install required packages. Please install manually:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete! You can now run the dashboard:")
    print("   python multi_tab_dashboard.py")
    print("   Then open http://localhost:8050 in your browser")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()
