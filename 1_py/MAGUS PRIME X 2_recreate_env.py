"""
Script to create a fresh virtual environment and install required packages
"""
import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command with description and error handling"""
    print(f"\n>>> {description}...")
    try:
        subprocess.check_call(cmd)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("=== MAGUS PRIME X Environment Recreation Tool ===")
    print("This script will create a fresh virtual environment with required packages.")
    
    # Get the current directory
    current_dir = os.getcwd()
    
    # Define the path for the new environment
    env_name = "magus_fresh_env"
    env_path = os.path.join(current_dir, env_name)
    
    # Create the virtual environment
    if not run_command(
        [sys.executable, "-m", "venv", env_path],
        "Creating virtual environment"
    ):
        return 1
    
    # Get the path to the Python executable in the new environment
    if os.name == 'nt':  # Windows
        python_path = os.path.join(env_path, "Scripts", "python.exe")
        pip_path = os.path.join(env_path, "Scripts", "pip.exe")
    else:  # Unix-like
        python_path = os.path.join(env_path, "bin", "python")
        pip_path = os.path.join(env_path, "bin", "pip")
    
    # Ensure the environment's pip is up to date
    if not run_command(
        [python_path, "-m", "pip", "install", "--upgrade", "pip"], 
        "Upgrading pip"
    ):
        return 1
    
    # Install required packages
    packages = [
        "black",
        "ruff",
        "pre-commit",
        "platformdirs",
        # Add other essential packages for your project
    ]
    
    for package in packages:
        if not run_command(
            [python_path, "-m", "pip", "install", package],
            f"Installing {package}"
        ):
            print(f"⚠️ Failed to install {package}, continuing with other packages...")
    
    # Success message
    print("\n=== Setup Complete ===")
    print(f"Your new environment is ready at: {env_path}")
    print("\nTo activate the new environment:")
    if os.name == 'nt':  # Windows
        print(f"    {env_name}\\Scripts\\activate")
    else:  # Unix-like
        print(f"    source {env_name}/bin/activate")
    
    print("\nAfter activation, you can use the coding tools:")
    print("    python -m black your_file.py")
    print("    python -m ruff check your_file.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
