#!/usr/bin/env python3
"""
Build script to create executables for Madden Franchise Event Generator
"""

import os
import sys
import platform
import subprocess
import importlib.util
import shutil
from datetime import datetime

def get_version():
    """Get version from version.txt file"""
    try:
        with open('version.txt', 'r') as f:
            version = f.read().strip()
        return version
    except FileNotFoundError:
        print("Warning: version.txt not found, using '0.1' as default")
        return "0.1"

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller>=5.6.0"])
        print("PyInstaller successfully installed.")
    else:
        print("PyInstaller is already installed.")

def check_icon_tools():
    """Check for and install necessary tools for icon conversion"""
    if platform.system() == "Windows":
        try:
            import PIL
            print("Pillow is already installed.")
        except ImportError:
            print("Installing Pillow for icon conversion...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("Pillow successfully installed.")
    elif platform.system() == "Darwin":  # macOS
        # Check if we have the iconutil command (comes with macOS)
        try:
            subprocess.run(["which", "iconutil"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("iconutil is available.")
        except subprocess.CalledProcessError:
            print("Warning: iconutil not found. This is needed for .icns conversion.")
            print("Please ensure your macOS developer tools are installed.")
            
        # Install imagemagick if not present
        try:
            subprocess.run(["which", "convert"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("ImageMagick is available.")
        except subprocess.CalledProcessError:
            print("ImageMagick not found. Please install it with:")
            print("brew install imagemagick")
            # We'll continue anyway, user can install later

def create_platform_icons():
    """Create platform-specific icons from the logo1.png file"""
    logo_path = os.path.join("resources", "logo1.png")
    if not os.path.exists(logo_path):
        print(f"Warning: {logo_path} not found. Icons will not be created.")
        return None, None, None
    
    print(f"Creating platform icons from {logo_path}...")
    
    # Paths for the platform-specific icons
    ico_path = os.path.join("resources", "app_icon.ico")
    icns_path = os.path.join("resources", "app_icon.icns")
    png_path = os.path.join("resources", "app_icon.png")
    
    # Copy logo1.png to app_icon.png
    shutil.copy2(logo_path, png_path)
    print(f"Created {png_path}")
    
    system = platform.system()
    
    # Create Windows .ico
    if system == "Windows":
        try:
            from PIL import Image
            img = Image.open(logo_path)
            # Create Windows icon with multiple sizes
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            print(f"Created {ico_path}")
        except Exception as e:
            print(f"Error creating .ico file: {e}")
            ico_path = None
    else:
        # On non-Windows, just note that .ico can't be created
        print("Note: .ico files can only be created on Windows.")
        ico_path = None
    
    # Create macOS .icns
    if system == "Darwin":  # macOS
        try:
            # Create a temporary iconset directory
            iconset_dir = os.path.join("resources", "app.iconset")
            os.makedirs(iconset_dir, exist_ok=True)
            
            # Generate different size icons
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            for size in sizes:
                output_name = f"icon_{size}x{size}.png"
                output_path = os.path.join(iconset_dir, output_name)
                subprocess.run([
                    "sips", "-z", str(size), str(size), 
                    logo_path, "--out", output_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # For Retina displays
                if size <= 512:  # Don't create 2048x2048
                    output_name_2x = f"icon_{size}x{size}@2x.png"
                    output_path_2x = os.path.join(iconset_dir, output_name_2x)
                    double_size = size * 2
                    subprocess.run([
                        "sips", "-z", str(double_size), str(double_size), 
                        logo_path, "--out", output_path_2x
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Convert the iconset to icns
            subprocess.run([
                "iconutil", "-c", "icns", iconset_dir, 
                "-o", icns_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Remove the temporary iconset directory
            shutil.rmtree(iconset_dir)
            print(f"Created {icns_path}")
        except Exception as e:
            print(f"Error creating .icns file: {e}")
            icns_path = None
    else:
        # On non-macOS, just note that .icns can't be created
        print("Note: .icns files can only be created on macOS.")
        icns_path = None
    
    return ico_path, icns_path, png_path

def create_all_platform_directories(version):
    """Create directories for all platforms"""
    platforms = {
        "windows": ".exe",
        "macos": ".app",
        "linux": ""
    }
    
    current_system = platform.system()
    if current_system == "Windows":
        current_platform = "windows"
    elif current_system == "Darwin":
        current_platform = "macos"
    else:
        current_platform = "linux"
    
    # Create directories for all platforms
    for platform_name, exe_extension in platforms.items():
        platform_dir = os.path.join("builds", version, platform_name)
        os.makedirs(platform_dir, exist_ok=True)
        
        # If not current platform, create placeholder README
        if platform_name != current_platform:
            readme_path = os.path.join(platform_dir, "BUILD_INSTRUCTIONS.txt")
            with open(readme_path, 'w') as f:
                f.write(f"Madden Franchise Generator v{version} - {platform_name.capitalize()} Build Instructions\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"This directory is a placeholder for the {platform_name.capitalize()} build.\n\n")
                f.write("To create the executable for this platform:\n")
                f.write(f"1. Copy this project to a {platform_name.capitalize()} machine\n")
                f.write("2. Run: python3 build_executable.py\n")
                f.write(f"3. The {platform_name.capitalize()} executable will be created in this directory\n\n")
                f.write("Note: You must build on the target platform, as cross-compilation is not supported by PyInstaller.\n")
    
    return current_platform

def build_executable():
    """Build the executable using PyInstaller"""
    # Get version
    version = get_version()
    print(f"Building version {version}")
    
    # Create directories for all platforms
    current_platform = create_all_platform_directories(version)
    
    # Create platform-specific icons
    ico_path, icns_path, png_path = create_platform_icons()
    
    # Determine platform-specific settings
    system = platform.system()
    
    if system == "Windows":
        icon_file = ico_path if ico_path else None
        exe_extension = ".exe"
        platform_name = "windows"
    elif system == "Darwin":  # macOS
        icon_file = icns_path if icns_path else None
        exe_extension = ".app"
        platform_name = "macos"
    else:  # Linux
        icon_file = png_path if png_path else None
        exe_extension = ""
        platform_name = "linux"
    
    # Create build directory structure
    build_dir = os.path.join("builds", version, platform_name)
    
    # Base name for the application with version
    app_name = f"Madden Franchise Generator v{version}"
    
    # Pass version to the executable
    with open('madden_franchise_qt/version.py', 'w') as f:
        f.write(f'VERSION = "{version}"\n')
    
    # Build the PyInstaller command using Python module execution
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", app_name,
        "--windowed",
        "--onedir",
        f"--distpath={build_dir}"
    ]
    
    # Add data files
    # Include the events.json template
    cmd.extend(["--add-data", f"madden_franchise_qt/data/events.json{os.pathsep}madden_franchise_qt/data"])
    
    # Include version.txt
    cmd.extend(["--add-data", f"version.txt{os.pathsep}."])
    
    # Include the resources folder with logo
    cmd.extend(["--add-data", f"resources{os.pathsep}resources"])
    
    # Cleanup flag
    cmd.append("--clean")
    
    # Add icon if available
    if icon_file:
        cmd.extend(["--icon", icon_file])
        print(f"Using icon: {icon_file}")
    else:
        print("No platform-specific icon available, using default.")
    
    # Add the main script
    cmd.append("run_madden_events.py")
    
    # Create necessary empty directories for packaging
    os.makedirs("madden_franchise_qt/data", exist_ok=True)
    os.makedirs("madden_franchise_qt/saves", exist_ok=True)
    
    # Execute the build command
    print(f"Building executable for {system}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        
        # Provide output location information
        if system == "Windows":
            exe_dir = os.path.join(build_dir, app_name)
            exe_path = os.path.join(exe_dir, f"{app_name}.exe")
        elif system == "Darwin":
            exe_dir = os.path.join(build_dir, f"{app_name}.app")
            exe_path = exe_dir  # For macOS, the .app folder is the executable
            
            # Create a boot script for macOS to fix pop-up dialogs
            print("Creating macOS boot script to fix pop-up dialogs...")
            boot_script_dir = os.path.join("build", app_name, "runtime_hooks")
            os.makedirs(boot_script_dir, exist_ok=True)
            
            boot_script_path = os.path.join(boot_script_dir, "mac_fix.py")
            with open(boot_script_path, "w") as f:
                f.write("import os\n")
                f.write("# Fix for Qt dialogs on macOS\n")
                f.write("os.environ['QT_MAC_WANTS_LAYER'] = '1'\n")
            
            # Add the boot script to the command
            cmd.extend(["--runtime-hook", boot_script_path])
        else:
            exe_dir = os.path.join(build_dir, app_name)
            exe_path = os.path.join(exe_dir, app_name)
        
        if os.path.exists(exe_dir):
            print(f"\nBuild successful! Application created at: {os.path.abspath(exe_dir)}")
            
            # Create a ZIP archive for easy distribution
            zip_name = f"{app_name}_{platform_name}.zip"
            zip_path = os.path.join(build_dir, zip_name)
            
            print(f"Creating ZIP archive: {zip_path}")
            if system == "Windows":
                import zipfile
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(exe_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, build_dir)
                            zipf.write(file_path, arcname)
            else:
                # Use shutil make_archive for Unix systems
                shutil.make_archive(
                    os.path.join(build_dir, app_name + "_" + platform_name),
                    'zip',
                    build_dir,
                    os.path.basename(exe_dir)
                )
            
            print(f"ZIP archive created at: {os.path.abspath(zip_path)}")
            
            # Create a README in the build directory
            readme_path = os.path.join(build_dir, "README.txt")
            with open(readme_path, 'w') as f:
                f.write(f"Madden Franchise Generator v{version}\n")
                f.write(f"Built on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for {system}\n\n")
                f.write("TO RUN THE APPLICATION:\n")
                f.write("=======================\n")
                if system == "Windows":
                    f.write(f"1. Extract the ZIP archive '{zip_name}' to any location\n")
                    f.write(f"2. Open the extracted folder and double-click '{app_name}.exe'\n")
                elif system == "Darwin":
                    f.write(f"1. Extract the ZIP archive '{zip_name}' to any location\n")
                    f.write(f"2. Double-click the extracted '{app_name}.app' file\n")
                    f.write("3. If you get a security warning, right-click the app and select 'Open'\n")
                else:
                    f.write(f"1. Extract the ZIP archive '{zip_name}' to any location\n")
                    f.write(f"2. Open the extracted folder and run: ./{app_name}\n")
                    f.write(f"   (You may need to make it executable first: chmod +x {app_name})\n")
                
                f.write("\nPORTABILITY NOTES:\n")
                f.write("=================\n")
                f.write("This application is designed to be portable and can be run from any location:\n")
                f.write("- You can copy the entire extracted folder to a USB drive or any directory\n")
                f.write("- The application will always store save files in the user data directory\n\n")
                
                f.write("SAVE FILES AND CONFIGURATION:\n")
                f.write("===========================\n")
                if system == "Windows":
                    save_location = r"C:\Users\{username}\AppData\Local\MaddenTools\MaddenFranchiseGenerator"
                elif system == "Darwin":
                    save_location = r"/Users/{username}/Library/Application Support/MaddenTools/MaddenFranchiseGenerator"
                else:
                    save_location = r"~/.local/share/MaddenTools/MaddenFranchiseGenerator"
                
                f.write(f"Your save files will be stored in: {save_location}\n")
                f.write("This location is created automatically when you run the application\n")
                f.write("If you need to backup your save files, this is where to find them\n")
            
            print(f"Created README at: {os.path.abspath(readme_path)}")
            
            # Create a builds/_latest directory with a copy of the latest build
            latest_dir = os.path.join("builds", "_latest")
            os.makedirs(latest_dir, exist_ok=True)
            
            latest_file = os.path.join(latest_dir, f"Madden_Franchise_Generator_{platform_name}_latest{exe_extension}")
            
            # If it's a directory (like .app bundle), use shutil.copytree
            if system == "Darwin" and exe_path.endswith(".app"):
                if os.path.exists(latest_file):
                    shutil.rmtree(latest_file, ignore_errors=True)
                shutil.copytree(exe_path, latest_file)
            else:
                if os.path.exists(latest_file):
                    os.remove(latest_file)
                shutil.copy2(exe_path, latest_file)
            
            print(f"Latest build also available at: {os.path.abspath(latest_file)}")
            
            # Create a summary file with build status for all platforms
            summary_file = os.path.join("builds", version, "BUILD_STATUS.txt")
            with open(summary_file, 'w') as f:
                f.write(f"Madden Franchise Generator v{version} - Build Status\n")
                f.write("=" * 50 + "\n\n")
                
                platforms = ["windows", "macos", "linux"]
                for plat in platforms:
                    if plat == platform_name:
                        f.write(f"✅ {plat.capitalize()}: Built successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    else:
                        f.write(f"❌ {plat.capitalize()}: Not built yet. Run build_executable.py on a {plat.capitalize()} machine.\n")
                
                f.write("\nTo complete all builds, run this script on each platform type.\n")
                f.write("Once all builds are complete, collect them in one place for distribution.\n")
            
            print(f"\nBuild status summary created at: {os.path.abspath(summary_file)}")
            print("\nTo build for all platforms, run this script on Windows, macOS, and Linux machines.")
            
        else:
            print("\nBuild completed, but executable wasn't found at the expected location.")
            print(f"Check the '{build_dir}' directory for your executable.")
    
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        print(f"Command output: {e.output if hasattr(e, 'output') else 'No output available'}")

if __name__ == "__main__":
    # Create resources directory if it doesn't exist
    os.makedirs("resources", exist_ok=True)
    
    # Check for PyInstaller
    check_pyinstaller()
    
    # Check for icon conversion tools
    check_icon_tools()
    
    # Check if appdirs is installed
    if importlib.util.find_spec("appdirs") is None:
        print("appdirs is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "appdirs>=1.4.4"])
        print("appdirs successfully installed.")
    
    # Build the executable
    build_executable() 