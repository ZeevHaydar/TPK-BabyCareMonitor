import subprocess
import sys

def install_packages(package_names):
    for package_name in package_names:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except subprocess.CalledProcessError as e:
            print(f"Error installing package {package_name}: {e}")
            sys.exit(1)

def update_requirements():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "freeze", "> requirements.txt"], shell=True)
        print("Requirements updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating requirements: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_install.py <package_name1> <package_name2> ...")
        sys.exit(1)

    package_names = sys.argv[1:]

    install_packages(package_names)
    update_requirements()
