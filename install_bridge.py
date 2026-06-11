#!/usr/bin/env python3
"""
Installer script for the Claude Chrome Extension Native Messaging Host Bridge
Automatically detects the Claude extension ID and installs the bridge manifest
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path

def get_chrome_extension_dir():
    """Get the Chrome extensions directory based on the platform"""
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        # Windows: %LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions
        local_app_data = os.getenv('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "Extensions"
        else:
            # Fallback
            return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Extensions"

    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/Google/Chrome/Default/Extensions
        return home / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Extensions"

    else:  # Linux and others
        # Linux: ~/.config/google-chrome/Default/Extensions
        # Also check for Chromium: ~/.config/chromium/Default/Extensions
        chrome_path = home / ".config" / "google-chrome" / "Default" / "Extensions"
        chromium_path = home / ".config" / "chromium" / "Default" / "Extensions"

        if chrome_path.exists():
            return chrome_path
        elif chromium_path.exists():
            return chromium_path
        else:
            # Default to Chrome path
            return chrome_path

def find_claude_extension_id(extensions_dir):
    """Find the Claude extension ID by looking for the extension name"""
    if not extensions_dir.exists():
        print(f"Extensions directory not found: {extensions_dir}")
        return None

    print(f"Searching for Claude extension in: {extensions_dir}")

    # Look through each extension directory
    for extension_dir in extensions_dir.iterdir():
        if not extension_dir.is_dir():
            continue

        # Look for manifest.json in the extension directory
        manifest_file = extension_dir / "manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)

                # Check if this is the Claude extension
                name = manifest.get("name", "")
                if "Claude" in name and ("Claude" == name or "Claude" in name):
                    print(f"Found Claude extension: {name} (ID: {extension_dir.name})")
                    return extension_dir.name

            except (json.JSONDecodeError, KeyError, IOError) as e:
                # Skip invalid manifests
                continue

    print("Claude extension not found in the extensions directory")
    return None

def get_native_messaging_hosts_dir():
    """Get the native messaging hosts directory based on the platform"""
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        # Windows: %LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts
        local_app_data = os.getenv('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts"
        else:
            return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts"

    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/Google/Chrome/NativeMessagingHosts
        return home / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts"

    else:  # Linux and others
        # Linux: ~/.config/google-chrome/NativeMessagingHosts
        # Also check for system-wide: /etc/opt/chrome/native-messaging-hosts
        chrome_dir = home / ".config" / "google-chrome" / "NativeMessagingHosts"
        system_dir = Path("/etc/opt/chrome/native-messaging-hosts")

        # Use user directory if it exists or can be created, otherwise try system
        if chrome_dir.exists() or os.access(home / ".config" / "google-chrome", os.W_OK):
            return chrome_dir
        elif system_dir.exists() or os.access(Path("/etc/opt/chrome"), os.W_OK):
            return system_dir
        else:
            # Default to Chrome user directory
            return chrome_dir

def create_manifest(extension_id, bridge_path):
    """Create the native messaging host manifest"""
    manifest = {
        "name": "com.anthropic.claude_browser_extension",
        "description": "Bridge connecting Claude Chrome extension to free-claude-code proxy",
        "path": str(bridge_path.absolute()),
        "type": "stdio",
        "allowed_origins": [
            f"chrome-extension://{extension_id}/"
        ]
    }
    return manifest

def main():
    print("Claude Chrome Extension Bridge Installer")
    print("=" * 50)

    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    bridge_path = script_dir / "claude_bridge.py"

    # Verify the bridge exists
    if not bridge_path.exists():
        print(f"Error: Bridge script not found at {bridge_path}")
        print("Please make sure claude_bridge.py is in the same directory as this installer.")
        return 1

    # Make sure bridge is executable
    if not os.access(bridge_path, os.X_OK):
        try:
            bridge_path.chmod(0o755)  # rwxr-xr-x
            print(f"Made bridge script executable: {bridge_path}")
        except Exception as e:
            print(f"Warning: Could not make bridge script executable: {e}")

    # Find Chrome extensions directory
    extensions_dir = get_chrome_extension_dir()
    if not extensions_dir:
        print("Error: Could not determine Chrome extensions directory")
        return 1

    print(f"Chrome extensions directory: {extensions_dir}")

    # Find the Claude extension ID
    extension_id = find_claude_extension_id(extensions_dir)
    if not extension_id:
        print("\nCould not automatically find the Claude extension.")
        print("Please make sure the Claude extension is installed in Chrome.")
        print("\nTo manually find your extension ID:")
        print("1. Open Chrome and go to chrome://extensions")
        print("2. Enable 'Developer mode' in the top-right corner")
        print("3. Find the Claude extension in the list")
        print("4. Look for the ID under the extension name (it looks like: abcdefghijklmnopqrstuvwxyz123456)")
        print("\nOnce you have the ID, you can:")
        print(f"  1. Edit the manifest manually or")
        print(f"  2. Re-run this script and provide the ID when prompted")

        # Ask if user wants to enter ID manually
        try:
            response = input("\nDo you want to enter the extension ID manually? (y/n): ").lower().strip()
            if response == 'y' or response == 'yes':
                extension_id = input("Enter the Claude extension ID: ").strip()
                if not extension_id:
                    print("Error: Extension ID cannot be empty")
                    return 1
                # Validate ID format (should be 32 lowercase letters/numbers)
                if len(extension_id) == 32 and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789' for c in extension_id):
                    print(f"Using extension ID: {extension_id}")
                else:
                    print("Warning: Extension ID doesn't look like a standard Chrome extension ID")
                    print("Continuing anyway...")
            else:
                return 1
        except KeyboardInterrupt:
            print("\nInstallation cancelled.")
            return 1

    # Get native messaging hosts directory
    hosts_dir = get_native_messaging_hosts_dir()
    print(f"\nNative messaging hosts directory: {hosts_dir}")

    try:
        # Create the directory if it doesn't exist
        hosts_dir.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {hosts_dir}")
    except Exception as e:
        print(f"Error: Could not create directory {hosts_dir}: {e}")
        return 1

    # Create manifest file path
    manifest_path = hosts_dir / "com.anthropic.claude_browser_extension.json"

    # Create the manifest
    manifest = create_manifest(extension_id, bridge_path)

    try:
        # Write the manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\nSuccessfully created manifest: {manifest_path}")
        print(f"Manifest contents:")
        print(json.dumps(manifest, indent=2))

    except Exception as e:
        print(f"Error: Could not write manifest file: {e}")
        return 1

    # Provide final instructions
    print("\n" + "=" * 50)
    print("INSTALLATION COMPLETE")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Make sure your free-claude-code server is running:")
    print("   fcc-server --host 127.0.0.1 --port 8082")
    print("   (Adjust port if needed - edit claude_bridge.py if using different port)")
    print("\n2. Restart Chrome completely (close all Chrome windows and reopen)")
    print("\n3. Test the connection:")
    print("   - Press Ctrl+E (or Command+E on Mac) to open the Claude sidepanel")
    print("   - The extension should connect successfully")
    print("   - Try sending a message to verify it works")
    print("\n4. Configure your external provider in free-claude-code:")
    print("   - Set environment variables or edit .env file for your provider")
    print("   - Example for NVIDIA NIM: export NVIDIA_NIM_API_KEY='your-key-here'")
    print("\nTroubleshooting:")
    print("- If connection fails, check that free-claude-code server is running")
    print("- Verify the bridge can reach the server: curl http://127.0.0.1:8082/")
    print("- Check bridge logs if you run it manually for debugging")
    print("- Ensure you have API keys configured for your chosen external provider")

    return 0

if __name__ == "__main__":
    sys.exit(main())