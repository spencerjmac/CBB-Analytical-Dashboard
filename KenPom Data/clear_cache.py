"""
Utility script to clear Python cache files that might cause stale code execution.
Run this if you're experiencing issues with old code being executed.
"""
import os
import shutil
import glob

def clear_python_cache():
    """Clear all __pycache__ directories and .pyc files."""
    cache_dirs = []
    pyc_files = []
    
    # Find all __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            cache_dirs.append(cache_path)
        # Find .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    # Remove cache directories
    removed_dirs = 0
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            removed_dirs += 1
            print(f"Removed: {cache_dir}")
        except Exception as e:
            print(f"Error removing {cache_dir}: {e}")
    
    # Remove .pyc files
    removed_files = 0
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            removed_files += 1
            print(f"Removed: {pyc_file}")
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")
    
    print(f"\nCleared {removed_dirs} cache directories and {removed_files} .pyc files")
    print("Python will regenerate cache files on next run with fresh code.")

if __name__ == "__main__":
    print("Clearing Python cache files...")
    clear_python_cache()
    print("\nDone! You can now run your scraper and it will use the latest code.")


