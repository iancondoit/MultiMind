#!/usr/bin/env python3
"""
Replace HSA-Ready Data

This script replaces the contents of the hsa-ready folder with the
clean, restructured data from hsa-ready-clean.
"""

import os
import sys
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hsa_replacer")

def backup_original(src_dir):
    """Create a backup of the original hsa-ready directory."""
    src_path = Path(src_dir)
    if not src_path.exists():
        logger.warning(f"Source directory {src_dir} does not exist, nothing to backup")
        return

    backup_dir = src_path.parent / f"{src_path.name}-original-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"Creating backup of {src_dir} to {backup_dir}")
    shutil.copytree(src_path, backup_dir)
    logger.info(f"Backup completed: {backup_dir}")
    return backup_dir

def clean_directory(directory):
    """Remove all contents from a directory, keeping the directory itself."""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.info(f"Creating directory {directory}")
        dir_path.mkdir(parents=True, exist_ok=True)
        return
    
    logger.info(f"Cleaning directory {directory}")
    
    # Remove all contents except .gitkeep
    for item in dir_path.glob('*'):
        if item.name == '.gitkeep':
            continue
        
        if item.is_file():
            item.unlink()
            logger.debug(f"Deleted file: {item}")
        elif item.is_dir():
            shutil.rmtree(item)
            logger.debug(f"Deleted directory: {item}")

def copy_directory_contents(src_dir, dst_dir):
    """Copy all contents from src_dir to dst_dir."""
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    if not src_path.exists():
        logger.error(f"Source directory {src_dir} does not exist")
        return False
    
    logger.info(f"Copying contents from {src_dir} to {dst_dir}")
    
    # Create directories if they don't exist
    dst_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all items except .gitkeep
    for item in src_path.glob('*'):
        if item.name == '.gitkeep':
            continue
            
        dst_item = dst_path / item.name
        
        if item.is_file():
            shutil.copy2(item, dst_item)
            logger.debug(f"Copied file: {item.name}")
        elif item.is_dir():
            shutil.copytree(item, dst_item)
            logger.debug(f"Copied directory: {item.name}")
    
    # Make sure .gitkeep exists in destination
    gitkeep_file = dst_path / '.gitkeep'
    if not gitkeep_file.exists():
        with open(gitkeep_file, 'w') as f:
            pass
        logger.debug(f"Created .gitkeep file")
    
    return True

def count_files(directory, extension='.json'):
    """Count files with a specific extension in a directory and its subdirectories."""
    count = 0
    for path in Path(directory).rglob(f'*{extension}'):
        if path.is_file():
            count += 1
    return count

def main():
    """Main function."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Replace HSA-ready data with cleaned version")
    parser.add_argument("--source", default="output/hsa-ready-clean", help="Source directory with clean data")
    parser.add_argument("--target", default="output/hsa-ready", help="Target directory to replace")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup of original data")
    args = parser.parse_args()
    
    # Count files before operation
    source_files = count_files(args.source)
    logger.info(f"Source directory has {source_files} JSON files")
    
    if not args.skip_backup:
        backup_dir = backup_original(args.target)
        if backup_dir:
            backup_files = count_files(backup_dir)
            logger.info(f"Backup directory has {backup_files} JSON files")
    
    # Clean target directory
    clean_directory(args.target)
    
    # Copy contents from source to target
    success = copy_directory_contents(args.source, args.target)
    
    if success:
        # Count files after operation
        target_files = count_files(args.target)
        logger.info(f"Target directory now has {target_files} JSON files")
        
        if target_files == source_files:
            logger.info("✅ Replacement complete and verified")
            return 0
        else:
            logger.error(f"❌ File count mismatch: source had {source_files}, target has {target_files}")
            return 1
    else:
        logger.error("❌ Replacement failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 