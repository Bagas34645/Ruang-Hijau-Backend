#!/usr/bin/env python3
"""
Database Package Verification Script
Verify all database files are present and properly configured
"""

import os
import sys
from pathlib import Path

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

def check_file(filename, description, required=True):
    """Check if a file exists"""
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        size_kb = size / 1024
        print_success(f"{description}: {size_kb:.1f} KB")
        return True
    else:
        if required:
            print_error(f"{description}: NOT FOUND")
        else:
            print_warning(f"{description}: NOT FOUND (optional)")
        return False

def main():
    print_header("Ruang Hijau Database Package Verification")
    
    # File list
    files_to_check = [
        # SQL Files (Required)
        ("ruang_hijau_database.sql", "Main Database Schema", True),
        ("ruang_hijau_advanced_features.sql", "Advanced Features (Views/Procedures)", False),
        ("ruang_hijau_test_queries.sql", "Test Queries", False),
        
        # Python Files (Required)
        ("db_helper.py", "Python Database Helper", True),
        
        # Config Files
        (".env.example", "Environment Config Template", True),
        
        # Documentation Files
        ("README_DATABASE.md", "Main Database README", True),
        ("QUICK_IMPLEMENTATION.md", "Quick Implementation Guide", True),
        ("SETUP_DATABASE.md", "Setup Instructions", True),
        ("DATABASE_DOCUMENTATION.md", "Complete Database Documentation", True),
        ("API_DATABASE_INTEGRATION.md", "API Integration Guide", True),
        ("DATABASE_FILES_SUMMARY.md", "Files Summary", True),
        ("INVENTORY.md", "Package Inventory", True),
    ]
    
    # Check files
    print_info("Checking Database Files...\n")
    
    found_count = 0
    required_count = 0
    missing_required = []
    
    for filename, description, required in files_to_check:
        if required:
            required_count += 1
        
        if check_file(filename, description, required):
            found_count += 1
        else:
            if required:
                missing_required.append(filename)
    
    # Summary
    print_header("Verification Summary")
    
    print(f"Files Found: {found_count}/{required_count} required")
    
    if missing_required:
        print_error(f"Missing {len(missing_required)} required file(s):")
        for f in missing_required:
            print(f"  - {f}")
    else:
        print_success("All required files present!")
    
    # Check Python packages
    print_info("\nChecking Python Dependencies...\n")
    
    packages = [
        ("mysql.connector", "mysql-connector-python"),
        ("dotenv", "python-dotenv"),
        ("flask", "flask"),
        ("flask_cors", "flask-cors"),
    ]
    
    missing_packages = []
    
    for module, package_name in packages:
        try:
            __import__(module)
            print_success(f"{package_name} installed")
        except ImportError:
            print_warning(f"{package_name} NOT installed")
            missing_packages.append(package_name)
    
    if missing_packages:
        print_warning(f"\nTo install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")
    
    # Check .env file
    print_info("\nChecking Configuration...\n")
    
    if os.path.exists(".env"):
        print_success(".env file exists (configured)")
    else:
        if os.path.exists(".env.example"):
            print_warning(".env file not found")
            print_info("To create .env file:")
            print("  cp .env.example .env")
            print("  # Then edit .env with your MySQL credentials")
        else:
            print_error(".env.example not found")
    
    # Final status
    print_header("Status")
    
    if not missing_required and not missing_packages:
        print_success("All checks passed! Database package is ready to use.")
        return 0
    else:
        if missing_required:
            print_error(f"{len(missing_required)} required file(s) missing")
        if missing_packages:
            print_error(f"{len(missing_packages)} Python package(s) missing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
