#!/usr/bin/env python3
"""
CodeRound Startup Discovery - Initialization Helper
Helps verify the project setup and configuration
"""

import os
import sys
import json
from pathlib import Path

def check_environment():
    """Check if all required files and directories exist"""
    
    print("=" * 60)
    print("CodeRound Startup Discovery - Setup Verification")
    print("=" * 60)
    
    checks = {
        "Frontend": [
            ("frontend/package.json", "Frontend dependencies"),
            ("frontend/pages/index.tsx", "Landing page"),
            ("frontend/lib/api.ts", "API client"),
            ("frontend/.env.example", "Frontend env template"),
        ],
        "Backend": [
            ("backend/requirements.txt", "Backend dependencies"),
            ("backend/main.py", "Backend entry point"),
            ("backend/models.py", "Database models"),
            ("backend/.env.example", "Backend env template"),
        ],
        "Database": [
            ("database/schema.sql", "Database schema"),
        ],
        "Documentation": [
            ("README.md", "Project README"),
            ("QUICKSTART.md", "Quick start guide"),
            ("docs/SETUP.md", "Setup guide"),
            ("docs/API.md", "API documentation"),
            ("DEPLOYMENT_CHECKLIST.md", "Deployment checklist"),
        ]
    }
    
    all_ok = True
    
    for category, files in checks.items():
        print(f"\n✓ {category}")
        for filepath, description in files:
            full_path = Path(filepath)
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"  ✓ {description:40} ({filepath})")
            else:
                print(f"  ✗ {description:40} ({filepath}) [MISSING]")
                all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✓ All project files are present!")
        print("\nNext steps:")
        print("1. Read QUICKSTART.md for 5-minute setup")
        print("2. Configure .env files with API keys")
        print("3. Create MySQL database from schema.sql")
        print("4. Install dependencies (pip, npm)")
        print("5. Run backend and frontend")
        return 0
    else:
        print("✗ Some files are missing!")
        print("Please check the listed files above")
        return 1

if __name__ == "__main__":
    sys.exit(check_environment())
