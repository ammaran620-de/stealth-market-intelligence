"""
Quick Start Script - Test the system quickly
"""
import sys
import os

print("🚀 Stealth Market Intelligence Engine - Quick Test\n")
print("This script will test your setup without running the full pipeline.\n")

# Check Python version
print("1. Checking Python version...")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8+ required")
    sys.exit(1)
print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

# Check dependencies
print("\n2. Checking dependencies...")
required_packages = [
    'playwright',
    'fake_useragent',
    'streamlit',
    'plotly',
    'pandas'
]

missing = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ❌ {package} not found")
        missing.append(package)

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Check Playwright browsers
print("\n3. Checking Playwright browsers...")
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
            browser.close()
            print("   ✓ Chromium browser installed")
        except Exception as e:
            print("   ❌ Chromium not found")
            print("   Run: playwright install chromium")
            sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Check .env file
print("\n4. Checking configuration...")
if os.path.exists('.env'):
    print("   ✓ .env file found")
    from dotenv import load_dotenv
    load_dotenv()
    
    ai_provider = os.getenv('AI_PROVIDER', 'openai')
    if ai_provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
    else:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key and api_key != 'your_openai_api_key_here' and api_key != 'your_anthropic_api_key_here':
        print(f"   ✓ {ai_provider.upper()} API key configured")
    else:
        print(f"   ⚠️  {ai_provider.upper()} API key not set (AI enrichment will fail)")
        print("   Edit .env file and add your API key")
else:
    print("   ⚠️  .env file not found")
    print("   Run: copy .env.example .env")
    print("   Then edit .env with your API keys")

# Check output directory
print("\n5. Checking output directory...")
if os.path.exists('output'):
    print("   ✓ Output directory exists")
else:
    print("   ⚠️  Output directory missing (will be created)")

print("\n" + "="*60)
print("✅ SETUP CHECK COMPLETE")
print("="*60)
print("\n📝 Next Steps:")
print("   1. Test scraping: python main.py --max-products 10")
print("   2. View dashboard: streamlit run dashboard/app.py")
print("   3. Read documentation: README.md")
print()
