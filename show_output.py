"""Display system capabilities and output summary"""
import json
from config.scraping_config import ScrapingConfig

print("\n" + "="*70)
print("🎯 STEALTH MARKET INTELLIGENCE ENGINE - OUTPUT SUMMARY")
print("="*70 + "\n")

# Show available targets
print("📋 CONFIGURED TARGETS:\n")
for target_name in ScrapingConfig.get_all_targets():
    config = ScrapingConfig.get_target_config(target_name)
    print(f"  • {target_name}")
    print(f"    URL: {config['url']}")
    print(f"    Type: {config['type']}")
    print()

# Show raw data
print("="*70)
print("📦 RAW SCRAPED DATA (output/products_raw.json)")
print("="*70 + "\n")

try:
    with open('output/products_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"Total Products: {raw_data['metadata']['total_products']}")
    print(f"Scraped At: {raw_data['metadata']['scraped_at']}")
    print(f"\nSample Products (first 3):\n")
    
    for product in raw_data['products'][:3]:
        print(f"  📖 {product['name']}")
        print(f"     Price: ${product['price']}")
        print(f"     Stock: {product['stock_info']['raw_text']}")
        print(f"     Source: {product['source']}")
        print()

except FileNotFoundError:
    print("⚠️  No raw data file found. Run: python main.py\n")

# Show enriched data
print("="*70)
print("🤖 AI-ENRICHED DATA (output/products_enriched.json)")
print("="*70 + "\n")

try:
    with open('output/products_enriched.json', 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    metadata = enriched_data['metadata']
    print(f"Total Products: {metadata['total_products']}")
    print(f"AI Provider: {metadata['ai_provider'].upper()}")
    print(f"Enriched At: {metadata['enriched_at']}")
    
    print(f"\n📊 Category Distribution:")
    for category, count in metadata['category_distribution'].items():
        print(f"   • {category}: {count} products")
    
    print(f"\nSample Enriched Products:\n")
    
    for product in enriched_data['products'][:3]:
        print(f"  📖 {product['name']}")
        print(f"     Price: ${product['price']}")
        print(f"     Category: {product['ai_category']}")
        print(f"     Reasoning: {product['ai_reasoning']}")
        print()

except FileNotFoundError:
    print("⚠️  No enriched data file found.\n")

print("="*70)
print("🚀 SYSTEM CAPABILITIES")
print("="*70 + "\n")

print("✅ Stealth Browser Automation")
print("   • Anti-bot detection scripts")
print("   • User-agent rotation")
print("   • Realistic HTTP headers\n")

print("✅ Human Behavior Simulation")
print("   • Random scrolling (200-600px increments)")
print("   • Mouse movements")
print("   • Reading delays (2-5 seconds)\n")

print("✅ Resilient Data Extraction")
print("   • Graceful error handling")
print("   • Price/rating normalization")
print("   • Stock scarcity detection\n")

print("✅ AI-Powered Enrichment")
print("   • OpenAI & Anthropic support")
print("   • Automatic categorization (Budget/Mid/High End)")
print("   • Fallback rule-based logic\n")

print("✅ Professional Dashboard")
print("   • Interactive Plotly charts")
print("   • Price/rating filters")
print("   • CSV export functionality\n")

print("="*70)
print("📝 NEXT STEPS")
print("="*70 + "\n")

print("1. Run full scraping pipeline:")
print("   python main.py --max-products 50\n")

print("2. Scrape different targets:")
print("   python main.py --target amazon_headphones\n")

print("3. Add real API key for AI enrichment:")
print("   Edit .env file and add OPENAI_API_KEY or ANTHROPIC_API_KEY\n")

print("4. Launch dashboard (if Streamlit is in PATH):")
print("   streamlit run dashboard/app.py")
print("   OR: python -m streamlit run dashboard/app.py\n")

print("="*70 + "\n")
