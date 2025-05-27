#!/usr/bin/env python3
"""
Verify Data Protection Script

This script verifies that your valuable downloaded newspaper data is properly
protected from being indexed by Cursor or committed to git.
"""

import os
import subprocess
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return its size."""
    path = Path(filepath)
    if path.exists():
        if path.is_file():
            size = path.stat().st_size
            return True, f"{size:,} bytes"
        else:
            return True, "directory"
    return False, "not found"

def count_cache_files():
    """Count files in the cache directory."""
    cache_dir = Path("cache")
    if not cache_dir.exists():
        return 0, "0 bytes"
    
    try:
        # Count .txt files
        txt_files = list(cache_dir.glob("*.txt"))
        
        # Get directory size
        result = subprocess.run(["du", "-sh", "cache/"], 
                              capture_output=True, text=True)
        size = result.stdout.split()[0] if result.returncode == 0 else "unknown"
        
        return len(txt_files), size
    except Exception as e:
        return 0, f"error: {e}"

def check_ignore_patterns():
    """Check if cache patterns are in ignore files."""
    patterns_to_check = ["cache/", "*.txt"]
    
    results = {}
    
    # Check .cursorignore
    cursor_ignore = Path(".cursorignore")
    if cursor_ignore.exists():
        content = cursor_ignore.read_text()
        results[".cursorignore"] = {
            pattern: pattern in content for pattern in patterns_to_check
        }
    else:
        results[".cursorignore"] = "file not found"
    
    # Check .gitignore
    git_ignore = Path(".gitignore")
    if git_ignore.exists():
        content = git_ignore.read_text()
        results[".gitignore"] = {
            pattern: pattern in content for pattern in patterns_to_check
        }
    else:
        results[".gitignore"] = "file not found"
    
    return results

def main():
    print("=" * 60)
    print("DATA PROTECTION VERIFICATION")
    print("=" * 60)
    
    # Check cache directory
    file_count, cache_size = count_cache_files()
    print(f"📁 Cache Directory:")
    print(f"   Files: {file_count:,} .txt files")
    print(f"   Size: {cache_size}")
    print()
    
    # Check ignore files
    print("🛡️  Protection Status:")
    ignore_results = check_ignore_patterns()
    
    for ignore_file, patterns in ignore_results.items():
        print(f"   {ignore_file}:")
        if isinstance(patterns, dict):
            for pattern, found in patterns.items():
                status = "✅ PROTECTED" if found else "❌ NOT PROTECTED"
                print(f"     {pattern}: {status}")
        else:
            print(f"     {patterns}")
    print()
    
    # Check for potential indexing directories
    print("🔍 Indexing Check:")
    cursor_dirs = list(Path(".").glob("**/.cursor*"))
    vscode_dirs = list(Path(".").glob("**/.vscode*"))
    
    if cursor_dirs or vscode_dirs:
        print("   ⚠️  Found potential indexing directories:")
        for d in cursor_dirs + vscode_dirs:
            print(f"     {d}")
    else:
        print("   ✅ No indexing directories found")
    print()
    
    # Summary
    print("📊 SUMMARY:")
    if file_count > 0:
        print(f"   ✅ {file_count:,} files successfully downloaded ({cache_size})")
    else:
        print("   ❌ No cache files found")
    
    # Check if all protections are in place
    all_protected = True
    for ignore_file, patterns in ignore_results.items():
        if isinstance(patterns, dict):
            if not all(patterns.values()):
                all_protected = False
        else:
            all_protected = False
    
    if all_protected:
        print("   ✅ All data properly protected from indexing")
        print("   ✅ Safe to continue working in Cursor")
    else:
        print("   ⚠️  Some protection patterns missing")
        print("   ⚠️  Risk of Cursor indexing large files")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 