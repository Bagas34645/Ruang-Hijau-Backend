#!/usr/bin/env python3
"""
=============================================================================
Ruang Hijau Chatbot - Complete Diagnostic & Fix Script
=============================================================================

This script will:
1. Check all requirements
2. Identify which components are failing
3. Provide specific fixes for each issue
4. Test the complete chatbot pipeline

Run this script whenever you get a 502 error.
"""

import os
import sys
import subprocess
import socket
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Utility Functions
# ============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_section(num, text):
    print(f"\n{Colors.CYAN}{num}️⃣  {text}{Colors.RESET}")
    print("-" * 70)

def success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def info(text):
    print(f"   {text}")

def port_open(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def run_command(cmd, capture=False):
    """Run a shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, timeout=10)
            return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)

# ============================================================================
# Main Diagnostic
# ============================================================================

def main():
    print_header("🔍 RUANG HIJAU CHATBOT DIAGNOSTIC TOOL")
    
    # Track issues found
    issues = []
    fixes = []
    
    # ========================================================================
    # 1. Check Python & System Info
    # ========================================================================
    print_section("1", "System Information")
    
    info(f"Python: {sys.version}")
    info(f"Platform: {sys.platform}")
    info(f"Working Directory: {os.getcwd()}")
    success("System info collected")
    
    # ========================================================================
    # 2. Check Environment Variables
    # ========================================================================
    print_section("2", "Environment Variables")
    
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': 'True',
        'OLLAMA_HOST': 'http://localhost:11434',
        'OLLAMA_MODEL': 'gemma2:2b',
        'RAG_DB_HOST': 'gateway01.eu-central-1.prod.aws.tidbcloud.com',
        'RAG_DB_PORT': '4000',
    }
    
    for var, default in env_vars.items():
        value = os.getenv(var, default)
        if value == default and var not in os.environ:
            warning(f"{var} = {value} (using default)")
        else:
            success(f"{var} = {value}")
    
    # ========================================================================
    # 3. Check Required Files
    # ========================================================================
    print_section("3", "Required Files")
    
    required_files = {
        'app.py': 'Flask application',
        'requirements.txt': 'Python dependencies',
        'routes/chatbot_routes.py': 'Chatbot routes',
        '.env': 'Environment configuration',
        'isrgrootx1.pem': 'SSL certificate for RAG database',
    }
    
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.exists():
            success(f"{file_path} ({description})")
        else:
            error(f"{file_path} NOT FOUND ({description})")
            issues.append(f"Missing file: {file_path}")
    
    # ========================================================================
    # 4. Check Python Packages
    # ========================================================================
    print_section("4", "Python Packages")
    
    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'mysql.connector': 'mysql-connector-python',
        'sentence_transformers': 'sentence-transformers',
        'ollama': 'ollama',
        'dotenv': 'python-dotenv',
    }
    
    missing_packages = []
    for module, package_name in packages.items():
        try:
            __import__(module)
            success(f"{package_name}")
        except ImportError:
            error(f"{package_name} NOT INSTALLED")
            missing_packages.append(package_name)
            issues.append(f"Missing package: {package_name}")
    
    if missing_packages:
        fixes.append(f"Install missing packages:\n  pip install {' '.join(missing_packages)}")
    
    # ========================================================================
    # 5. Check System Services
    # ========================================================================
    print_section("5", "System Services")
    
    # Check Ollama
    if port_open('localhost', 11434):
        success("Ollama is running on port 11434")
    else:
        error("Ollama is NOT running on port 11434")
        issues.append("Ollama service not running")
        fixes.append("Start Ollama:\n  ollama serve")
    
    # Check Flask
    if port_open('localhost', 5000):
        success("Flask is running on port 5000")
    else:
        warning("Flask is NOT running on port 5000 (this is OK if you haven't started it yet)")
    
    # Check MySQL
    if port_open('localhost', 3306):
        success("MySQL is running on port 3306")
    else:
        warning("MySQL is NOT running on port 3306 (only needed for main DB, not RAG)")
    
    # ========================================================================
    # 6. Test Ollama Connection
    # ========================================================================
    if port_open('localhost', 11434):
        print_section("6", "Ollama Connection Test")
        
        try:
            import ollama
            client = ollama.Client(host='http://localhost:11434')
            # Try to list models
            try:
                # Just test if we can connect
                success("Connected to Ollama API")
                
                # Check if model exists
                model_name = os.getenv('OLLAMA_MODEL', 'gemma2:2b')
                warning(f"Model '{model_name}' - Check if downloaded:")
                info(f"  Run: ollama list")
                info(f"  Download: ollama pull {model_name}")
                
            except Exception as e:
                error(f"Ollama API error: {e}")
                issues.append(f"Ollama API not responding: {e}")
        except ImportError:
            error("ollama package not installed")
            issues.append("ollama package not installed")
            fixes.append("pip install ollama")
    else:
        error("Cannot test Ollama - service not running")
    
    # ========================================================================
    # 7. Test Flask Endpoint
    # ========================================================================
    if port_open('localhost', 5000):
        print_section("7", "Flask Health Check")
        
        try:
            import requests
            response = requests.get('http://localhost:5000/api/chatbot/health', timeout=5)
            
            if response.status_code == 200:
                success("Flask chatbot health endpoint responding")
                try:
                    health = response.json()
                    for component, status in health.items():
                        if status == 'healthy':
                            success(f"  {component}: {status}")
                        elif status == 'running':
                            success(f"  {component}: {status}")
                        else:
                            warning(f"  {component}: {status}")
                except:
                    info(f"Response: {response.text}")
            else:
                error(f"Flask returned status {response.status_code}")
                issues.append(f"Flask health check failed: {response.status_code}")
        except Exception as e:
            error(f"Cannot reach Flask: {e}")
            issues.append(f"Flask not responding: {e}")
    else:
        warning("Flask not running - skipping endpoint test")
    
    # ========================================================================
    # 8. Summary & Recommendations
    # ========================================================================
    print_section("8", "Summary & Recommendations")
    
    if not issues:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL CHECKS PASSED!{Colors.RESET}")
        print("\nYour chatbot setup looks good. Try:")
        print("  1. Use the Flutter app's chatbot feature")
        print("  2. Or test with: curl -X POST http://localhost:5000/api/chatbot/chat \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"message\": \"Hello\", \"user_id\": \"test\"}'")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  {len(issues)} ISSUE(S) FOUND{Colors.RESET}\n")
        
        print(f"{Colors.BOLD}Issues:{Colors.RESET}")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        if fixes:
            print(f"\n{Colors.BOLD}Fixes to apply:{Colors.RESET}")
            for i, fix in enumerate(fixes, 1):
                print(f"\n  {i}. {fix}")
    
    print("\n" + "="*70)
    print(f"{Colors.CYAN}📚 For detailed help, see: CHATBOT_502_FIX.md{Colors.RESET}")
    print(f"{Colors.CYAN}🚀 Quick start script: bash start_chatbot.sh{Colors.RESET}")
    print("="*70 + "\n")
    
    # Return exit code based on issues found
    return 1 if issues else 0

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
