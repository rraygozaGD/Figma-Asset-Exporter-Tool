# Quick Start Guide - Figma Image Importer

## 🚀 Option 1: Automated Setup (Recommended for Windows)

1. **Download/Clone the project** to your computer
2. **Double-click `quick-start.bat`** - this will:
   - Create a Python virtual environment
   - Install all dependencies
   - Show you next steps

## 🛠️ Option 2: Manual Setup

### Step 1: Prerequisites
- Ensure Python 3.7+ is installed
- Get your Figma API token from https://www.figma.com/settings

### Step 2: Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration
```bash
# Run the interactive setup
python setup.py
```

OR manually edit `config/settings.py`:
```python
FIGMA_API_TOKEN = "your-token-here"
FIGMA_FILE_KEY = "your-file-key-here"
DOWNLOAD_PATH = r"C:\path\to\output"
```

### Step 4: Run the Application
```bash
python src/main.py
```

## 📋 What You Need

1. **Figma API Token**
   - Go to https://www.figma.com/settings
   - Create a "Personal access token"
   - Copy the token

2. **Figma File Key**
   - From your Figma URL: `https://www.figma.com/file/[FILE_KEY]/...`


## 📁 Output

- **Images**: Saved to your specified download directory
- **Logs**: Check the `logs/` folder for detailed information

## 🔧 Troubleshooting

1. **Python not found**: Make sure Python is installed and in your PATH
2. **Permission errors**: Run as administrator or check file permissions
3. **API errors**: Verify your token and file key are correct
4. **No images found**: Check logs for filtering information

## 📞 Need Help?

1. Check the full `README.md` for detailed documentation
2. Review log files in the `logs/` directory
3. Test with the provided test scripts

## 🎯 What Gets Downloaded

- ✅ Embedded bitmap images (PNG, JPG, etc.)
- ✅ Vector components and icons 
- ✅ Frames and groups (if appropriately sized)
- ✅ Elements with export settings
- ❌ Invalid image references (automatically filtered)
- ❌ Corrupted node IDs (automatically filtered)

---

**That's it!** The application includes smart filtering to handle the 400 error issues you were experiencing. It will automatically skip problematic image references and node IDs while processing all valid content.
