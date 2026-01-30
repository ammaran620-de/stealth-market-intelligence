"""
Professional Streamlit Dashboard for Market Intelligence Visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.scraping_config import ScrapingConfig


class MarketIntelligenceDashboard:
    """
    Client-ready dashboard for visualizing market intelligence data
    """
    
    def __init__(self):
        self.data_path = ScrapingConfig.OUTPUT_PATHS['enriched_data']
        self.df = None
        self.metadata = None
    
    def load_data(self) -> bool:
        """Load enriched data from JSON"""
        if not os.path.exists(self.data_path):
            return False
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get('metadata', {})
            products = data.get('products', [])
            
            if not products:
                return False
            
            # Convert to DataFrame
            self.df = pd.DataFrame(products)
            
            # Clean and prepare data
            self.df = self.df[self.df['price'].notna()]  # Filter out null prices
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False
    
    def render(self):
        """Render the complete dashboard"""
        
        # Page configuration
        st.set_page_config(
            page_title="Market Intelligence Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for professional look
        st.markdown("""
            <style>
            .main {
                background-color: #f5f7fa;
            }
            .stMetric {
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1f2937;
                font-weight: 700;
            }
            h2, h3 {
                color: #374151;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.title("🎯 Market Intelligence Dashboard")
        st.markdown("**AI-Powered E-Commerce Competitor Analysis**")
        st.divider()
        
        # Load data
        if not self.load_data():
            st.error("❌ No enriched data found. Please run the scraper first.")
            st.info("💡 Run: `python main.py` to collect and enrich data")
            return
        
        # Sidebar filters
        self._render_sidebar()
        
        # Apply filters
        filtered_df = self._apply_filters()
        
        if filtered_df.empty:
            st.warning("No products match the selected filters.")
            return
        
        # Main dashboard sections
        self._render_metrics(filtered_df)
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_price_distribution(filtered_df)
            self._render_rating_analysis(filtered_df)
        
        with col2:
            self._render_category_breakdown(filtered_df)
            self._render_price_vs_rating(filtered_df)
        
        st.divider()
        self._render_product_table(filtered_df)
    
    def _render_sidebar(self):
        """Render sidebar with filters"""
        st.sidebar.header("🔍 Filters")
        
        # Metadata info
        if self.metadata:
            st.sidebar.info(f"""
            **Data Info:**
            - Total Products: {self.metadata.get('total_products', 'N/A')}
            - AI Provider: {self.metadata.get('ai_provider', 'N/A').upper()}
            - Enriched: {self.metadata.get('enriched_at', 'N/A')[:10]}
            """)
        
        st.sidebar.divider()
        
        # Price range filter
        if 'price' in self.df.columns and not self.df['price'].isna().all():
            min_price = float(self.df['price'].min())
            max_price = float(self.df['price'].max())
            
            st.sidebar.subheader("💰 Price Range")
            price_range = st.sidebar.slider(
                "Select price range",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
                format="$%.2f"
            )
            st.session_state['price_range'] = price_range
        
        # Category filter
        if 'ai_category' in self.df.columns:
            st.sidebar.subheader("📦 Category")
            categories = ['All'] + sorted(self.df['ai_category'].dropna().unique().tolist())
            selected_category = st.sidebar.selectbox("Select category", categories)
            st.session_state['category'] = selected_category
        
        # Rating filter
        if 'rating' in self.df.columns and not self.df['rating'].isna().all():
            st.sidebar.subheader("⭐ Minimum Rating")
            min_rating = st.sidebar.slider(
                "Select minimum rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5
            )
            st.session_state['min_rating'] = min_rating
    
    def _apply_filters(self) -> pd.DataFrame:
        """Apply selected filters to dataframe"""
        df = self.df.copy()
        
        # Price filter
        if 'price_range' in st.session_state:
            min_p, max_p = st.session_state['price_range']
            df = df[(df['price'] >= min_p) & (df['price'] <= max_p)]
        
        # Category filter
        if 'category' in st.session_state and st.session_state['category'] != 'All':
            df = df[df['ai_category'] == st.session_state['category']]
        
        # Rating filter
        if 'min_rating' in st.session_state:
            df = df[df['rating'] >= st.session_state['min_rating']]
        
        return df
    
    def _render_metrics(self, df: pd.DataFrame):
        """Render key metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📦 Total Products",
                value=len(df)
            )
        
        with col2:
            avg_price = df['price'].mean()
            st.metric(
                label="💵 Average Price",
                value=f"${avg_price:.2f}"
            )
        
        with col3:
            if 'rating' in df.columns:
                avg_rating = df['rating'].dropna().mean()
                st.metric(
                    label="⭐ Average Rating",
                    value=f"{avg_rating:.2f}/5.0"
                )
        
        with col4:
            price_range = df['price'].max() - df['price'].min()
            st.metric(
                label="📊 Price Range",
                value=f"${price_range:.2f}"
            )
    
    def _render_price_distribution(self, df: pd.DataFrame):
        """Render price distribution chart"""
        st.subheader("💰 Price Distribution")
        
        fig = px.histogram(
            df,
            x='price',
            nbins=30,
            title="Product Price Distribution",
            labels={'price': 'Price ($)', 'count': 'Number of Products'},
            color_discrete_sequence=['#3b82f6']
        )
        
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_category_breakdown(self, df: pd.DataFrame):
        """Render category breakdown chart"""
        st.subheader("📦 Category Breakdown")
        
        if 'ai_category' in df.columns:
            category_counts = df['ai_category'].value_counts()
            
            colors = {
                'Budget': '#10b981',
                'Mid Range': '#f59e0b',
                'High End': '#ef4444'
            }
            
            color_list = [colors.get(cat, '#6b7280') for cat in category_counts.index]
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=category_counts.index,
                    values=category_counts.values,
                    hole=0.4,
                    marker=dict(colors=color_list)
                )
            ])
            
            fig.update_layout(
                title="Products by Category",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    def _render_rating_analysis(self, df: pd.DataFrame):
        """Render rating analysis"""
        st.subheader("⭐ Rating Analysis")
        
        if 'rating' in df.columns and not df['rating'].isna().all():
            fig = px.box(
                df,
                y='rating',
                title="Rating Distribution",
                labels={'rating': 'Product Rating'},
                color_discrete_sequence=['#8b5cf6']
            )
            
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rating data available")
    
    def _render_price_vs_rating(self, df: pd.DataFrame):
        """Render price vs rating scatter plot"""
        st.subheader("💰 Price vs Rating Analysis")
        
        if 'rating' in df.columns and not df['rating'].isna().all():
            category_colors = {
                'Budget': '#10b981',
                'Mid Range': '#f59e0b',
                'High End': '#ef4444'
            }
            
            fig = px.scatter(
                df,
                x='price',
                y='rating',
                color='ai_category' if 'ai_category' in df.columns else None,
                title="Price vs Rating Correlation",
                labels={'price': 'Price ($)', 'rating': 'Rating', 'ai_category': 'Category'},
                color_discrete_map=category_colors,
                hover_data=['name']
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for correlation analysis")
    
    def _render_product_table(self, df: pd.DataFrame):
        """Render detailed product table"""
        st.subheader("📋 Detailed Product List")
        
        # Select relevant columns
        display_columns = ['name', 'price', 'rating', 'ai_category', 'ai_reasoning']
        available_columns = [col for col in display_columns if col in df.columns]
        
        display_df = df[available_columns].copy()
        
        # Format columns
        if 'price' in display_df.columns:
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
        
        if 'rating' in display_df.columns:
            display_df['rating'] = display_df['rating'].apply(lambda x: f"{x:.1f}⭐" if pd.notna(x) else "N/A")
        
        # Rename columns for display
        display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name="market_intelligence_data.csv",
            mime="text/csv"
        )


def main():
    """Main entry point for dashboard"""
    dashboard = MarketIntelligenceDashboard()
    dashboard.render()


if __name__ == "__main__":
    main()
