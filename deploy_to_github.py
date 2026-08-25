"""
GitHub Auto-Deploy Script for LexiSummarize
============================================
This script automatically:
1. Creates a new GitHub repository
2. Uploads ALL project files via GitHub REST API (no git needed!)
3. Prints the Streamlit Cloud deploy link

HOW TO USE:
1. Go to https://github.com/settings/tokens/new
2. Give it a name like "TextSummarizer"
3. Set expiration to 90 days
4. Under "Scopes", check: [x] repo (full control of private repositories)
5. Click "Generate token" and COPY the token
6. Paste it below where it says YOUR_TOKEN_HERE
7. Enter your GitHub username where it says YOUR_USERNAME_HERE
8. Run: python deploy_to_github.py
"""

import os
import base64
import requests
import json

# ==============================================================
# FILL IN THESE TWO VALUES BEFORE RUNNING
# ==============================================================
GITHUB_TOKEN    = "YOUR_TOKEN_HERE"       # Paste your token here
GITHUB_USERNAME = "YOUR_USERNAME_HERE"    # Your GitHub username
REPO_NAME       = "TextSummarizer"        # Name for the new repo
# ==============================================================

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Files and folders to include
INCLUDE_EXTENSIONS = {".py", ".txt", ".md", ".toml", ".json", ".cfg", ".ini", ""}
EXCLUDE_DIRS = {"__pycache__", ".git", "venv", "env", ".venv", "uploads", "outputs"}
EXCLUDE_FILES = {"tunnel.py", "deploy_to_github.py"}

def get_all_files(base_path):
    """Walk the directory and collect all files to upload."""
    files = []
    for root, dirs, filenames in os.walk(base_path):
        # Remove excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, base_path).replace("\\", "/")
            ext = os.path.splitext(filename)[1].lower()
            files.append((full_path, rel_path))
    return files

def create_repo():
    """Create a new public GitHub repository."""
    print(f"\n[1/3] Creating GitHub repository '{REPO_NAME}'...")
    url = "https://api.github.com/user/repos"
    payload = {
        "name": REPO_NAME,
        "description": "LexiSummarize: NLP-Based Extractive Text Summarizer (Streamlit App)",
        "private": False,
        "auto_init": False
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 201:
        print(f"    Repository created: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
        return True
    elif resp.status_code == 422:
        print(f"    Repository already exists - will update files.")
        return True
    else:
        print(f"    ERROR creating repo: {resp.status_code} - {resp.text}")
        return False

def upload_file(full_path, repo_path):
    """Upload a single file to the GitHub repository."""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{repo_path}"
    
    # Read file content
    try:
        with open(full_path, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode("utf-8")
    except Exception as e:
        print(f"    SKIP (read error): {repo_path} - {e}")
        return False
    
    # Check if file already exists (get SHA for update)
    sha = None
    check = requests.get(url, headers=HEADERS)
    if check.status_code == 200:
        sha = check.json().get("sha")
    
    payload = {
        "message": f"Add {repo_path}",
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha
    
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code in (200, 201):
        return True
    else:
        print(f"    ERROR uploading {repo_path}: {resp.status_code} - {resp.text[:200]}")
        return False

def main():
    if GITHUB_TOKEN == "YOUR_TOKEN_HERE":
        print("\n" + "="*60)
        print("  ERROR: You haven't filled in your GitHub token!")
        print("="*60)
        print("\nSteps:")
        print("  1. Go to: https://github.com/settings/tokens/new")
        print("  2. Name: TextSummarizer")
        print("  3. Expiration: 90 days")
        print("  4. Check the box: [x] repo")
        print("  5. Click Generate token -> Copy it")
        print("  6. Open this file and paste it in GITHUB_TOKEN = '...'")
        print("  7. Also fill in GITHUB_USERNAME")
        print("  8. Run again!")
        return
    
    if GITHUB_USERNAME == "YOUR_USERNAME_HERE":
        print("\nERROR: Please fill in your GitHub username in this file.")
        return
    
    # Verify token works
    me = requests.get("https://api.github.com/user", headers=HEADERS)
    if me.status_code != 200:
        print(f"\nERROR: Invalid token or network issue ({me.status_code})")
        print("Make sure your token has 'repo' scope enabled.")
        return
    actual_username = me.json()["login"]
    print(f"\nAuthenticated as: {actual_username}")
    
    # Create repository
    if not create_repo():
        return
    
    # Collect all files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = get_all_files(base_dir)
    total = len(all_files)
    print(f"\n[2/3] Uploading {total} files to GitHub...")
    
    success = 0
    for i, (full_path, rel_path) in enumerate(all_files, 1):
        print(f"    [{i}/{total}] {rel_path}", end=" ... ")
        ok = upload_file(full_path, rel_path)
        if ok:
            print("OK")
            success += 1
        
    print(f"\n[3/3] Upload complete! {success}/{total} files uploaded.")
    
    print("\n" + "="*60)
    print("  DEPLOY TO STREAMLIT CLOUD (FREE - 2 minutes):")
    print("="*60)
    print(f"\n  GitHub Repo:   https://github.com/{actual_username}/{REPO_NAME}")
    print(f"\n  1. Open:       https://share.streamlit.io/")
    print(f"  2. Click:      'New app'")
    print(f"  3. Repository: {actual_username}/{REPO_NAME}")
    print(f"  4. Branch:     main")
    print(f"  5. Main file:  app.py")
    print(f"  6. Click:      'Deploy!'")
    print(f"\n  Your permanent link will be:")
    print(f"  https://{REPO_NAME.lower()}.streamlit.app   (or similar)")
    print("="*60)

if __name__ == "__main__":
    main()
