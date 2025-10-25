import os
import language_tool_python

# Set your cache folder
CACHE_DIR = r"D:\languagetool_editor"
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ["LANGUAGETOOL_CACHE"] = CACHE_DIR

print("Downloading LanguageTool backend...")
tool = language_tool_python.LanguageTool('en-US')
print("✅ Download complete! Cached at:", CACHE_DIR)
