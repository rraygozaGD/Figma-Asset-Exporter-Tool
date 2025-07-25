# Figma Image Importer

A Python application that extracts and downloads images from Figma files, including both embedded bitmap images and exportable vector components.

## Features

- **Bitmap Image Extraction**: Downloads embedded images (PNG, JPG, etc.) from Figma files
- **Vector Component Export**: Exports components, frames, and icons as PNG images
- **Smart Filtering**: Automatically filters out invalid image references and node IDs that cause API errors
- **Intelligent Detection**: Identifies exportable elements based on size, type, and naming conventions
- **Comprehensive Logging**: Detailed logs for debugging and monitoring the extraction process
- **Error Handling**: Robust error handling with specific validation for Figma API requirements

## Prerequisites

- Python 3.7 or higher
- Figma API access token
- Internet connection for API requests

## Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <your-repository-url>
cd figma-importer

# Or download and extract the ZIP file
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install dependencies manually:

```bash
pip install requests
```

## Configuration

### 1. Get Figma API Token

1. Go to [Figma Settings](https://www.figma.com/settings)
2. Scroll down to "Personal access tokens"
3. Click "Create a new personal access token"
4. Give it a name and click "Create token"
5. Copy the token (you won't be able to see it again)

### 2. Configure the Application

Edit `config/settings.py` or set environment variables:

```python
# config/settings.py
FIGMA_API_TOKEN = "your-figma-api-token-here"
FIGMA_FILE_KEY = "your-figma-file-key-here"
DOWNLOAD_PATH = "path/to/download/folder"
```

Or set environment variables:

```bash
# Windows
set FIGMA_API_TOKEN=your-token-here
set FIGMA_FILE_KEY=your-file-key-here
set DOWNLOAD_PATH=C:\path\to\download

# macOS/Linux
export FIGMA_API_TOKEN=your-token-here
export FIGMA_FILE_KEY=your-file-key-here
export DOWNLOAD_PATH=/path/to/download
```

### 3. Get Figma File Key

The file key is found in the Figma URL:
```
https://www.figma.com/file/[FILE_KEY]/[FILE_NAME]
```

For example, if your URL is:
```
https://www.figma.com/file/testKeyFile/Design-System
```

Then your file key is: `testKeyFile`

## Usage

### Basic Usage

```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Run the application
python src/main.py
```

### Command Line Options

If your main script supports command line arguments:

```bash
# Specify file key directly
python src/main.py --file-key kFzFCcTt59Pj2juGcvytMo

# Specify output directory
python src/main.py --output-dir "C:\my-images"

# Enable debug logging
python src/main.py --debug
```

## Project Structure

```
figma-importer/
├── src/
│   ├── main.py              # Main application entry point
│   ├── figma_client.py      # Figma API client
│   ├── image_processor.py   # Image processing utilities
│   └── utils/
│       └── helpers.py       # Helper functions
├── config/
│   └── settings.py          # Configuration settings
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## What Gets Extracted

### 1. Bitmap Images
- Embedded PNG, JPG, and other raster images
- Images used in fills, effects, and strokes
- Only processes images with valid references (containing ':' or '-' separators)

### 2. Vector Components
- Components and component instances
- Frames and groups that meet size criteria (16x16 to 512x512 pixels)
- Elements with export settings
- Icons, logos, and symbols (detected by naming patterns)
- Vector compositions (groups with primarily vector elements)

## Filtering Logic

The application includes smart filtering to prevent API errors:

### Image Reference Filtering
- Removes image references without ':' or '-' separators
- These are typically invalid hash references that cause 400 errors

### Node ID Filtering
- Removes node IDs without ':' or '-' separators
- Ensures only valid Figma node IDs are sent to the API

## Troubleshooting

### Common Issues

1. **400 Bad Request Errors**
   - Usually caused by invalid node IDs or image references
   - The application now filters these out automatically
   - Check logs for details about filtered items

2. **Authentication Errors**
   - Verify your Figma API token is correct
   - Make sure the token has access to the file
   - Check if the file is public or shared with your account

3. **File Not Found**
   - Verify the file key is correct
   - Make sure the file exists and is accessible
   - Check if the file has been deleted or moved

4. **No Images Found**
   - The file might not contain extractable images
   - Check if the file has components or embedded images
   - Review the filtering logs to see what was excluded

### Debugging

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Log Files**
   - Logs are saved in the `logs/` directory
   - Each run creates a timestamped log file
   - Review logs for detailed extraction information

## API Rate Limits

- Figma API has rate limits (typically 1000 requests per hour)
- The application processes up to 100 nodes per request
- Large files may require multiple requests
- Monitor logs for rate limit warnings

## Output

### Downloaded Files
- Images are saved to the specified download directory
- Filenames include node names and IDs for easy identification
- Both bitmap images and exported vector components

### Log Files
- Detailed logs in the `logs/` directory
- Includes extraction statistics and error details
- Timestamped for easy tracking

## Support

For issues or questions:

1. Check the logs for detailed error information
2. Verify your Figma API token and file permissions
3. Test with the provided test scripts
4. Review the filtering logic if getting 400 errors

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
