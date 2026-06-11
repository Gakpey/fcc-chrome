# Claude Chrome Extension Bridge - Production Ready

This solution connects the Claude Chrome Extension to free-claude-code, enabling use of external AI providers (including NVIDIA NIM) without requiring a Claude subscription.

## Components

1. **claude_bridge.py** - Native messaging host bridge that connects the extension to free-claude-code HTTP server
2. **install_bridge.py** - Automated installer that detects the Claude extension and deploys the bridge
3. **Test suite** - Comprehensive tests verifying functionality

## Features

- ✅ Production-ready native messaging host implementation
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Automatic Claude extension detection
- ✅ Environment variable configuration
- ✅ Comprehensive logging (console and file)
- ✅ Graceful shutdown handling
- ✅ Binary-safe native messaging protocol implementation
- ✅ Error handling and validation
- ✅ Supports all free-claude-code features:
  - Ping/pong connectivity testing
  - Status reporting (native host installed, MCP connected)
  - Tool request handling
  - Audio notifications (OFFSCREEN_PLAY_SOUND)
  - GIF generation (GENERATE_GIF)
  - Extension internal messages

## How It Works

The Chrome Extension communicates with native messaging hosts using:
- 4-byte length prefix (little-endian unsigned int)
- JSON message payload
- stdin/stdout for communication

This bridge:
1. Reads messages from extension via stdin (binary protocol)
2. Parses JSON messages
3. Routes to appropriate handlers
4. Makes HTTP requests to free-claude-code server
5. Sends responses back to extension via stdout

## Installation

### Automatic Installation
```bash
python3 install_bridge.py
```

The installer will:
1. Detect your Chrome installation directory
2. Find the Claude extension by scanning manifests
3. Create the native messaging hosts directory
4. Generate the manifest pointing to claude_bridge.py
5. Make the bridge executable
6. Provide post-installation instructions

### Manual Installation
If automatic detection fails:
1. Find your Chrome extension ID at `chrome://extensions` (enable Developer mode)
2. Run: `python3 install_bridge.py` and enter the ID when prompted
3. Or manually create the manifest:
   ```json
   {
     "name": "com.anthropic.claude_browser_extension",
     "description": "Bridge connecting Claude Chrome extension to free-claude-code proxy",
     "path": "/full/path/to/claude_bridge.py",
     "type": "stdio",
     "allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID/"]
   }
   ```
   Save to:
   - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts\`
   - macOS: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
   - Linux: `~/.config/google-chrome/NativeMessagingHosts/`

## Configuration

Configure the bridge using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| FREE_CLAUDE_CODE_HOST | 127.0.0.1 | free-claude-code server hostname |
| FREE_CLAUDE_CODE_PORT | 8082 | free-claude-code server port |
| FREE_CLAUDE_CODE_API_KEY | freecc | API key for authentication |
| LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| LOG_TO_FILE | false | Enable file logging |
| LOG_FILE_PATH | (auto) | Log file path (defaults to ~/claude_bridge.log) |
| HTTP_TIMEOUT | 30 | HTTP request timeout in seconds |
| HEALTH_CHECK_ENDPOINT | / | Endpoint for health checks |
| STATUS_ENDPOINT | / | Endpoint for status checks |

### Example Usage
```bash
# Configure for NVIDIA NIM provider via free-claude-code
export FREE_CLAUDE_CODE_HOST=127.0.0.1
export FREE_CLAUDE_CODE_PORT=8082
export FREE_CLAUDE_CODE_API_KEY=freecc
export LOG_LEVEL=INFO
export LOG_TO_FILE=true

# Start free-claude-code server (in another terminal)
fcc-server --host 127.0.0.1 --port 8082

# The bridge will automatically start when the extension needs it
```

## Usage

1. Install the bridge using `python3 install_bridge.py`
2. Start your free-claude-code server:
   ```bash
   fcc-server --host 127.0.0.1 --port 8082
   ```
3. Configure your external provider in free-claude-code (e.g., set NVIDIA_NIM_API_KEY for NVIDIA NIM)
4. Restart Chrome completely
5. Press Ctrl+E (or Command+E on Mac) to open the Claude sidebar
6. The extension should connect successfully via the bridge

## Testing

Run the test suite to verify functionality:
```bash
python3 test_native_messaging.py      # Basic protocol tests
python3 test_tool_request.py         # Tool request handling
python3 test_audio_gif.py            # Audio and GIF functionality
python3 test_integration.py          # Full integration test
```

## Production Notes

- The bridge is designed to be lightweight and efficient
- Logging to file is disabled by default for performance (enable with LOG_TO_FILE=true)
- Message size is limited to 10MB for security
- Graceful shutdown handled via SIGTERM/SIGINT
- Automatic reconnection logic handled by the extension
- No modifications needed to the Chrome extension itself
- Works with any external provider supported by free-claude-code

## Troubleshooting

1. **Bridge not starting**: Check that free-claude-code server is running
2. **Connection failed**: Verify extension ID in manifest matches your installation
3. **No response**: Check bridge logs (stderr by default, or file if LOG_TO_FILE=true)
4. **Permission issues**: Ensure claude_bridge.py is executable (chmod +x)
5. **Extension not detecting bridge**: Restart Chrome completely after installation

## Supported Providers

Through free-claude-code, you can use any provider that implements an Anthropic-compatible API, including:
- NVIDIA NIM
- OpenAI
- Anthropic (direct)
- Hugging Face
- Local models (llama.cpp, etc.)
- And more...

Refer to the free-claude-code documentation for provider-specific configuration.