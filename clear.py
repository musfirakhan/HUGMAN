import os
import shutil
from pathlib import Path

def clean_output_folders(output_folder: str, animations_folder: str):
    """
    Clears all contents of output folder and removes .bvh/.glb files from animations folder
    
    Args:
        output_folder: Path to your output directory (will be completely cleared)
        animations_folder: Path to animations directory (only .bvh/.glb files removed)
    """
    try:
        print(f"Cleaning output folder: {output_folder}")
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            os.makedirs(output_folder)
            print("Output folder cleared successfully")
        else:
            print("Output folder doesn't exist, creating it")
            os.makedirs(output_folder)

        print(f"\n Cleaning animations folder: {animations_folder}")
        if os.path.exists(animations_folder):
            deleted_files = 0
            for file in Path(animations_folder).glob("*"):
                if file.suffix.lower() in ('.bvh', '.glb'):
                    try:
                        os.unlink(file)
                        print(f"  Deleted: {file.name}")
                        deleted_files += 1
                    except Exception as e:
                        print(f" Couldn't delete {file.name}: {e}")
            
            print(f"Removed {deleted_files} animation files")
        else:
            print("Animations folder doesn't exist, skipping")

    except Exception as e:
        print(f"\n Error during cleanup: {e}")
        return False
    
    print("\nCleanup completed")
    return True

if __name__ == "__main__":
    OUTPUT_FOLDER = "output"
    ANIMATIONS_FOLDER = "animations"
    
    success = clean_output_folders(OUTPUT_FOLDER, ANIMATIONS_FOLDER)
    exit(0 if success else 1)