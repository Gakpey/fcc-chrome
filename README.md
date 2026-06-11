# FCC-Chrome Bridge

Production-ready Native Messaging Host Bridge connecting Claude Chrome Extension to free-claude-code for external AI provider usage.

## Overview

This bridge enables the Claude Chrome Extension to work with external AI providers (like NVIDIA NIM, OpenAI, etc.) through the free-claude-code proxy, **without requiring a Claude subscription or login**.

## Key Features

- 🔌 Connects Chrome Extension to free-claude-code via native messaging
- 🌐 Supports any Anthropic-compatible API provider
- 💻 Cross-platform (Windows, macOS, Linux)
- 🔧 Automatic extension detection and installation
- ⚙️ Configurable via environment variables
- 📝 Comprehensive logging and error handling
- 🛡️ Production-ready with security considerations

## Quick Start

1. **Install the bridge:**
   ```bash
   python3 install_bridge.py
   ```

2. **Start free-claude-code server:**
   ```bash
   fcc-server --host 127.0.0.1 --port 8082
   ```

3. **Configure your external provider** (e.g., for NVIDIA NIM):
   ```bash
   export NVIDIA_NIM_API_KEY='your-api-key-here'
   ```

4. **Restart Chrome** and press `Ctrl+E` to use!

## Documentation

For detailed installation, configuration, usage, and troubleshooting guides, see [USAGE.md](USAGE.md).

## Components

- `claude_bridge.py` - The native messaging host bridge
- `install_bridge.py` - Automated installer with extension detection
- `USAGE.md` - Comprehensive documentation

## Testing

Run the test suite to verify functionality:
```bash
python3 test_native_messaging.py
python3 test_tool_request.py
python3 test_audio_gif.py
python3 test_integration.py
```

## License

MIT License - see [LICENSE](LICENSE) file.

---

**Note:** The test files are not included in this production repository. They were used during development and validation.