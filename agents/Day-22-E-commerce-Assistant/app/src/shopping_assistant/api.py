"""
FastAPI web interface for the shopping assistant
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Optional
import uuid

from .agent import ShoppingAssistant
from .models import (
    SearchQuery, SearchResult, ComparisonRequest, ComparisonResult,
    RecommendationRequest, ReviewSummary, PriceTracker, QueryType
)
from .database import init_database, get_db, SessionLocal, PriceTrackerDB

app = FastAPI(
    title="Shopping Assistant API",
    description="AI-powered e-commerce assistant for product search, comparison, and recommendations",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the shopping assistant
assistant = ShoppingAssistant()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopping Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .search-box { width: 100%; padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 20px; }
            .button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
            .button:hover { background: #0056b3; }
            .product-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: white; }
            .product-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; color: #333; }
            .product-price { font-size: 20px; color: #e74c3c; font-weight: bold; margin-bottom: 8px; }
            .product-rating { color: #f39c12; margin-bottom: 8px; }
            .product-features { margin-top: 10px; }
            .feature-tag { background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 12px; }
            .loading { text-align: center; color: #666; }
            .error { color: #e74c3c; background: #ffebee; padding: 10px; border-radius: 4px; margin: 10px 0; }
            .tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #ddd; }
            .tab { padding: 10px 20px; cursor: pointer; border-bottom: 2px solid transparent; }
            .tab.active { border-bottom-color: #007bff; color: #007bff; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛍️ AI Shopping Assistant</h1>
                <p>Search, compare, and get recommendations for products</p>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('search')">Search</div>
                <div class="tab" onclick="showTab('compare')">Compare</div>
                <div class="tab" onclick="showTab('recommend')">Recommend</div>
                <div class="tab" onclick="showTab('track')">Price Track</div>
            </div>
            
            <div id="search-tab" class="tab-content active">
                <input type="text" id="search-query" class="search-box" placeholder="Search for products... (e.g., 'red running shoes under $100')" onkeypress="if(event.key==='Enter') searchProducts()">
                <button class="button" onclick="searchProducts()">Search Products</button>
                <div id="search-results"></div>
            </div>
            
            <div id="compare-tab" class="tab-content">
                <textarea id="compare-urls" class="search-box" placeholder="Enter product URLs to compare, one per line" rows="4"></textarea>
                <button class="button" onclick="compareProducts()">Compare Products</button>
                <div id="compare-results"></div>
            </div>
            
            <div id="recommend-tab" class="tab-content">
                <input type="text" id="recommend-description" class="search-box" placeholder="Describe what you're looking for... (e.g., 'laptop for programming under $1000')">
                <input type="number" id="recommend-budget" class="search-box" placeholder="Budget (optional)">
                <input type="text" id="recommend-brands" class="search-box" placeholder="Preferred brands (comma-separated, optional)">
                <button class="button" onclick="getRecommendations()">Get Recommendations</button>
                <div id="recommend-results"></div>
            </div>
            
            <div id="track-tab" class="tab-content">
                <input type="text" id="track-url" class="search-box" placeholder="Product URL to track">
                <input type="number" id="track-price" class="search-box" placeholder="Target price" step="0.01">
                <input type="text" id="track-user" class="search-box" placeholder="Your email/user ID">
                <button class="button" onclick="trackPrice()">Start Tracking</button>
                <div id="track-results"></div>
            </div>
        </div>
        
        <script>
            function showTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
            }
            
            async function searchProducts() {
                const query = document.getElementById('search-query').value;
                if (!query) return;
                
                const resultsDiv = document.getElementById('search-results');
                resultsDiv.innerHTML = '<div class="loading">Searching for products...</div>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query, query_type: 'search', max_results: 10 })
                    });
                    
                    const data = await response.json();
                    displaySearchResults(data, resultsDiv);
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">Error searching products: ' + error.message + '</div>';
                }
            }
            
            function displaySearchResults(data, container) {
                if (!data.products || data.products.length === 0) {
                    container.innerHTML = '<div class="error">No products found.</div>';
                    return;
                }
                
                let html = `<h3>Found ${data.total_found} products (showing ${data.products.length})</h3>`;
                
                data.products.forEach(product => {
                    html += `
                        <div class="product-card">
                            <div class="product-title">${product.title}</div>
                            <div class="product-price">$${product.price ? product.price.toFixed(2) : 'N/A'}</div>
                            <div class="product-rating">⭐ ${product.rating || 'N/A'} (${product.review_count || 0} reviews)</div>
                            <div style="margin: 8px 0;"><strong>Brand:</strong> ${product.brand || 'N/A'}</div>
                            <div style="margin: 8px 0;"><strong>Source:</strong> ${product.source}</div>
                            ${product.description ? '<div style="margin: 8px 0; color: #666;">' + product.description + '</div>' : ''}
                            <div class="product-features">
                                ${product.features ? product.features.map(f => `<span class="feature-tag">${f}</span>`).join('') : ''}
                            </div>
                            <div style="margin-top: 10px;">
                                <a href="${product.url}" target="_blank" style="color: #007bff;">View Product →</a>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            async function compareProducts() {
                const urls = document.getElementById('compare-urls').value.split('\\n').filter(url => url.trim());
                if (urls.length < 2) {
                    alert('Please enter at least 2 product URLs to compare');
                    return;
                }
                
                const resultsDiv = document.getElementById('compare-results');
                resultsDiv.innerHTML = '<div class="loading">Comparing products...</div>';
                
                try {
                    const response = await fetch('/compare', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ product_urls: urls })
                    });
                    
                    const data = await response.json();
                    displayComparisonResults(data, resultsDiv);
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">Error comparing products: ' + error.message + '</div>';
                }
            }
            
            function displayComparisonResults(data, container) {
                let html = '<h3>Product Comparison</h3>';
                
                if (data.summary) {
                    html += `<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;"><strong>Analysis:</strong><br>${data.summary}</div>`;
                }
                
                data.products.forEach(product => {
                    html += `
                        <div class="product-card">
                            <div class="product-title">${product.title}</div>
                            <div class="product-price">$${product.price ? product.price.toFixed(2) : 'N/A'}</div>
                            <div class="product-rating">⭐ ${product.rating || 'N/A'}</div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            async function getRecommendations() {
                const description = document.getElementById('recommend-description').value;
                if (!description) return;
                
                const budget = document.getElementById('recommend-budget').value;
                const brands = document.getElementById('recommend-brands').value.split(',').map(b => b.trim()).filter(b => b);
                
                const resultsDiv = document.getElementById('recommend-results');
                resultsDiv.innerHTML = '<div class="loading">Getting recommendations...</div>';
                
                try {
                    const requestData = { description: description };
                    if (budget) requestData.budget = parseFloat(budget);
                    if (brands.length > 0) requestData.preferred_brands = brands;
                    
                    const response = await fetch('/recommend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestData)
                    });
                    
                    const data = await response.json();
                    displaySearchResults(data, resultsDiv);
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">Error getting recommendations: ' + error.message + '</div>';
                }
            }
            
            async function trackPrice() {
                const url = document.getElementById('track-url').value;
                const price = document.getElementById('track-price').value;
                const userId = document.getElementById('track-user').value;
                
                if (!url || !price || !userId) {
                    alert('Please fill in all fields');
                    return;
                }
                
                const resultsDiv = document.getElementById('track-results');
                resultsDiv.innerHTML = '<div class="loading">Setting up price tracking...</div>';
                
                try {
                    const response = await fetch('/track', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            user_id: userId, 
                            product_url: url, 
                            target_price: parseFloat(price) 
                        })
                    });
                    
                    const data = await response.json();
                    resultsDiv.innerHTML = `
                        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px;">
                            <strong>Price tracking started!</strong><br>
                            Product: ${data.product_title}<br>
                            Target Price: $${data.target_price}<br>
                            Current Price: $${data.current_price || 'N/A'}<br>
                            You'll be notified when the price drops below your target.
                        </div>
                    `;
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">Error setting up price tracking: ' + error.message + '</div>';
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/search", response_model=SearchResult)
async def search_products(query: SearchQuery):
    """Search for products"""
    try:
        results = assistant.search_products(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare", response_model=ComparisonResult)
async def compare_products(request: ComparisonRequest):
    """Compare multiple products"""
    try:
        results = assistant.compare_products(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend", response_model=SearchResult)
async def get_recommendations(request: RecommendationRequest):
    """Get personalized product recommendations"""
    try:
        results = assistant.get_recommendations(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/track", response_model=PriceTracker)
async def track_price(user_id: str, product_url: str, target_price: float):
    """Set up price tracking for a product"""
    try:
        tracker = assistant.track_price(user_id, product_url, target_price)
        return tracker
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/track/{user_id}", response_model=List[PriceTracker])
async def get_user_trackers(user_id: str):
    """Get all price trackers for a user"""
    try:
        with SessionLocal() as db:
            trackers = db.query(PriceTrackerDB).filter(
                PriceTrackerDB.user_id == user_id,
                PriceTrackerDB.is_active == True
            ).all()
            
            return [
                PriceTracker(
                    id=t.id,
                    user_id=t.user_id,
                    product_url=t.product_url,
                    product_title=t.product_title,
                    target_price=t.target_price,
                    current_price=t.current_price,
                    last_checked=t.last_checked,
                    created_at=t.created_at,
                    is_active=t.is_active
                )
                for t in trackers
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reviews/{product_url:path}", response_model=ReviewSummary)
async def get_review_summary(product_url: str):
    """Get summarized reviews for a product"""
    try:
        summary = assistant.summarize_reviews(product_url)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Shopping Assistant API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 