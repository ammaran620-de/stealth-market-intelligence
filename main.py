"""
Main Orchestrator - Production-grade entry point for Stealth Market Intelligence Engine
"""
import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.stealth_scraper import StealthScraper
from src.ai_enrichment import enrich_from_file
from config.scraping_config import ScrapingConfig


class MarketIntelligenceEngine:
    """
    Main orchestrator for the complete intelligence gathering pipeline
    """
    
    def __init__(self, target: str = 'books_toscrape', max_products: int = 50):
        self.target = target
        self.max_products = max_products
    
    def run_full_pipeline(self, skip_scraping: bool = False, skip_enrichment: bool = False):
        """
        Execute the complete pipeline: scrape → enrich → report
        
        Args:
            skip_scraping: Skip scraping step (use existing data)
            skip_enrichment: Skip AI enrichment step
        """
        print("\n" + "="*70)
        print("🚀 STEALTH MARKET INTELLIGENCE ENGINE")
        print("="*70 + "\n")
        
        # Step 1: Scraping
        if not skip_scraping:
            self._run_scraping()
        else:
            print("⏭️  Skipping scraping (using existing data)\n")
        
        # Step 2: AI Enrichment
        if not skip_enrichment:
            self._run_enrichment()
        else:
            print("⏭️  Skipping AI enrichment\n")
        
        # Step 3: Report
        self._generate_report()
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
        self._display_next_steps()
    
    def _run_scraping(self):
        """Execute scraping phase"""
        print("📊 PHASE 1: DATA COLLECTION")
        print("-" * 70)
        
        try:
            scraper = StealthScraper(target_name=self.target)
            products = scraper.scrape(max_products=self.max_products)
            
            if not products:
                print("❌ No products collected. Please check the target configuration.")
                sys.exit(1)
            
            scraper.save_to_json(products)
            print()
            
        except Exception as e:
            print(f"\n❌ Scraping failed: {e}")
            sys.exit(1)
    
    def _run_enrichment(self):
        """Execute AI enrichment phase"""
        print("🤖 PHASE 2: AI ENRICHMENT & CATEGORIZATION")
        print("-" * 70)
        
        try:
            enrich_from_file()
            print()
            
        except Exception as e:
            print(f"\n⚠️  AI enrichment failed: {e}")
            print("Continuing without enrichment...")
            print()
    
    def _generate_report(self):
        """Generate summary report"""
        print("📈 PHASE 3: SUMMARY REPORT")
        print("-" * 70)
        
        try:
            import json
            
            enriched_path = ScrapingConfig.OUTPUT_PATHS['enriched_data']
            
            if not os.path.exists(enriched_path):
                print("⚠️  No enriched data found for reporting")
                return
            
            with open(enriched_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            products = data.get('products', [])
            
            print(f"✓ Total Products Analyzed: {metadata.get('total_products', 0)}")
            print(f"✓ AI Provider: {metadata.get('ai_provider', 'N/A').upper()}")
            
            if 'category_distribution' in metadata:
                print(f"\n📦 Category Distribution:")
                for category, count in metadata['category_distribution'].items():
                    print(f"   • {category}: {count} products")
            
            # Price statistics
            prices = [p['price'] for p in products if p.get('price') is not None]
            if prices:
                print(f"\n💰 Price Analysis:")
                print(f"   • Lowest: ${min(prices):.2f}")
                print(f"   • Highest: ${max(prices):.2f}")
                print(f"   • Average: ${sum(prices)/len(prices):.2f}")
            
            print()
            
        except Exception as e:
            print(f"⚠️  Could not generate report: {e}\n")
    
    def _display_next_steps(self):
        """Display next steps for the user"""
        print("🎯 NEXT STEPS:")
        print("-" * 70)
        print("1. View data files:")
        print(f"   • Raw data: {ScrapingConfig.OUTPUT_PATHS['raw_data']}")
        print(f"   • Enriched data: {ScrapingConfig.OUTPUT_PATHS['enriched_data']}")
        print()
        print("2. Launch interactive dashboard:")
        print("   > streamlit run dashboard/app.py")
        print()
        print("3. Run for different targets:")
        available_targets = ScrapingConfig.get_all_targets()
        print(f"   Available: {', '.join(available_targets)}")
        print(f"   > python main.py --target <target_name>")
        print()


def main():
    """Main entry point with CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="Stealth Market Intelligence Engine - E-Commerce Competitor Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline on default target (books_toscrape)
  python main.py
  
  # Scrape Amazon headphones
  python main.py --target amazon_headphones --max-products 100
  
  # Skip scraping and only enrich existing data
  python main.py --skip-scraping
  
  # Run scraping only (no AI enrichment)
  python main.py --skip-enrichment
  
  # List available targets
  python main.py --list-targets
        """
    )
    
    parser.add_argument(
        '--target',
        type=str,
        default='books_toscrape',
        help='Target website to scrape (default: books_toscrape)'
    )
    
    parser.add_argument(
        '--max-products',
        type=int,
        default=50,
        help='Maximum number of products to scrape (default: 50)'
    )
    
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Skip scraping phase (use existing data)'
    )
    
    parser.add_argument(
        '--skip-enrichment',
        action='store_true',
        help='Skip AI enrichment phase'
    )
    
    parser.add_argument(
        '--list-targets',
        action='store_true',
        help='List all available scraping targets'
    )
    
    args = parser.parse_args()
    
    # Handle list targets
    if args.list_targets:
        print("\n📋 Available Scraping Targets:\n")
        for target_name in ScrapingConfig.get_all_targets():
            config = ScrapingConfig.get_target_config(target_name)
            print(f"  • {target_name}")
            print(f"    URL: {config['url']}")
            print(f"    Type: {config['type']}")
            print()
        return
    
    # Validate target
    if args.target not in ScrapingConfig.get_all_targets():
        print(f"❌ Error: Unknown target '{args.target}'")
        print(f"Available targets: {', '.join(ScrapingConfig.get_all_targets())}")
        print("Run with --list-targets to see details")
        sys.exit(1)
    
    # Run pipeline
    engine = MarketIntelligenceEngine(
        target=args.target,
        max_products=args.max_products
    )
    
    engine.run_full_pipeline(
        skip_scraping=args.skip_scraping,
        skip_enrichment=args.skip_enrichment
    )


if __name__ == "__main__":
    main()
