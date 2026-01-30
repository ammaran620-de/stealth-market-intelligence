"""
AI Intelligence & Enrichment Layer - LLM-powered data categorization and analysis
"""
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from config.scraping_config import ScrapingConfig


class AIEnrichmentEngine:
    """
    Handles AI-powered data enrichment using LLM APIs
    Decoupled design allows easy provider switching
    """
    
    def __init__(self, provider: str = None):
        self.config = ScrapingConfig.AI_CONFIG
        self.provider = provider or self.config['provider']
        self.client = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                api_key = self.config['openai_api_key']
                
                if not api_key or api_key == 'your_openai_api_key_here':
                    raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env")
                
                self.client = OpenAI(api_key=api_key)
                self.model = self.config['model_openai']
                print("✅ OpenAI client initialized")
                
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                api_key = self.config['anthropic_api_key']
                
                if not api_key or api_key == 'your_anthropic_api_key_here':
                    raise ValueError("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env")
                
                self.client = Anthropic(api_key=api_key)
                self.model = self.config['model_anthropic']
                print("✅ Anthropic client initialized")
                
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _call_llm(self, prompt: str) -> str:
        """
        Make LLM API call with provider abstraction
        
        Args:
            prompt: The prompt to send to the LLM
        
        Returns:
            LLM response text
        """
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert e-commerce data analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
            )
            return response.choices[0].message.content
        
        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    
    def categorize_products(self, products: List[Dict]) -> List[Dict]:
        """
        Categorize products into pricing tiers using AI
        
        Args:
            products: List of product dictionaries
        
        Returns:
            Enriched products with AI categorization
        """
        print("🤖 Starting AI enrichment process...")
        
        # Filter valid products with prices
        valid_products = [p for p in products if p.get('price') is not None]
        
        if not valid_products:
            print("⚠️  No valid products with prices to enrich")
            return products
        
        # Calculate price statistics for context
        prices = [p['price'] for p in valid_products]
        price_stats = {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices)
        }
        
        print(f"   Price range: ${price_stats['min']:.2f} - ${price_stats['max']:.2f} (avg: ${price_stats['avg']:.2f})")
        
        # Batch process products
        enriched_products = []
        batch_size = 20
        
        for i in range(0, len(valid_products), batch_size):
            batch = valid_products[i:i + batch_size]
            print(f"   Processing batch {i//batch_size + 1} ({len(batch)} products)...")
            
            enriched_batch = self._enrich_batch(batch, price_stats)
            enriched_products.extend(enriched_batch)
        
        # Merge back with invalid products
        all_products = enriched_products + [p for p in products if p.get('price') is None]
        
        print(f"✅ Enriched {len(enriched_products)} products")
        
        return all_products
    
    def _enrich_batch(self, products: List[Dict], price_stats: Dict) -> List[Dict]:
        """
        Enrich a batch of products with AI categorization
        
        Args:
            products: Batch of products
            price_stats: Price statistics for context
        
        Returns:
            Enriched product batch
        """
        # Prepare data for LLM
        product_summary = []
        for p in products:
            product_summary.append({
                'id': p['id'],
                'name': p['name'],
                'price': p['price'],
                'rating': p['rating']
            })
        
        prompt = f"""
Analyze these e-commerce products and categorize each into a pricing tier.

PRICE STATISTICS:
- Min: ${price_stats['min']:.2f}
- Max: ${price_stats['max']:.2f}
- Average: ${price_stats['avg']:.2f}

PRODUCTS:
{json.dumps(product_summary, indent=2)}

TASK:
For each product, determine its category based on:
1. Price relative to the range
2. Rating (if available)
3. Product name/features

CATEGORIES:
- "Budget" - Lower-priced options (typically below average)
- "Mid Range" - Moderately priced (around average)
- "High End" - Premium/expensive (well above average)

Respond ONLY with valid JSON in this exact format:
{{
  "categorizations": [
    {{
      "id": "product_id",
      "category": "Budget|Mid Range|High End",
      "reasoning": "brief explanation"
    }}
  ]
}}
"""
        
        try:
            # Call LLM
            response_text = self._call_llm(prompt)
            
            # Parse response
            response_json = json.loads(response_text)
            categorizations = {c['id']: c for c in response_json['categorizations']}
            
            # Enrich products
            enriched = []
            for product in products:
                product_copy = product.copy()
                
                if product['id'] in categorizations:
                    cat_data = categorizations[product['id']]
                    product_copy['ai_category'] = cat_data['category']
                    product_copy['ai_reasoning'] = cat_data['reasoning']
                else:
                    product_copy['ai_category'] = self._fallback_categorization(product, price_stats)
                    product_copy['ai_reasoning'] = "Fallback categorization based on price"
                
                product_copy['enriched_at'] = datetime.now().isoformat()
                enriched.append(product_copy)
            
            return enriched
            
        except Exception as e:
            print(f"   ⚠️  AI enrichment error: {e}")
            print("   Falling back to rule-based categorization...")
            
            # Fallback to rule-based
            return [self._apply_fallback(p, price_stats) for p in products]
    
    def _fallback_categorization(self, product: Dict, price_stats: Dict) -> str:
        """
        Rule-based fallback categorization when AI fails
        
        Args:
            product: Product dictionary
            price_stats: Price statistics
        
        Returns:
            Category string
        """
        price = product.get('price', 0)
        avg_price = price_stats['avg']
        
        if price < avg_price * 0.7:
            return "Budget"
        elif price < avg_price * 1.3:
            return "Mid Range"
        else:
            return "High End"
    
    def _apply_fallback(self, product: Dict, price_stats: Dict) -> Dict:
        """Apply fallback categorization to a product"""
        product_copy = product.copy()
        product_copy['ai_category'] = self._fallback_categorization(product, price_stats)
        product_copy['ai_reasoning'] = "Rule-based categorization (AI unavailable)"
        product_copy['enriched_at'] = datetime.now().isoformat()
        return product_copy
    
    def save_enriched_data(self, products: List[Dict], output_path: str = None):
        """
        Save enriched products to JSON
        
        Args:
            products: Enriched product list
            output_path: Output file path
        """
        output_path = output_path or ScrapingConfig.OUTPUT_PATHS['enriched_data']
        
        # Calculate statistics
        categories = {}
        for p in products:
            cat = p.get('ai_category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        output_data = {
            'metadata': {
                'total_products': len(products),
                'enriched_at': datetime.now().isoformat(),
                'ai_provider': self.provider,
                'category_distribution': categories
            },
            'products': products
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Enriched data saved to: {output_path}")
        print(f"📊 Category distribution: {categories}")


def enrich_from_file(input_path: str = None, output_path: str = None, provider: str = None):
    """
    Convenience function to enrich data from a JSON file
    
    Args:
        input_path: Input JSON file path
        output_path: Output JSON file path
        provider: AI provider ('openai' or 'anthropic')
    """
    input_path = input_path or ScrapingConfig.OUTPUT_PATHS['raw_data']
    
    print(f"📂 Loading data from: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', [])
    print(f"   Loaded {len(products)} products")
    
    # Initialize enrichment engine
    engine = AIEnrichmentEngine(provider=provider)
    
    # Enrich products
    enriched_products = engine.categorize_products(products)
    
    # Save results
    engine.save_enriched_data(enriched_products, output_path)
    
    return enriched_products
