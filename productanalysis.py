from flask import Flask, jsonify, render_template, request, redirect, url_for
from transformers import pipeline
import pandas as pd
import re
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Flask from environment variables
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Define product file paths
PRODUCT_FILES = {
    'firebolt': r"C:\Users\vijayk\Desktop\project\project\Fire-Boltt.csv",
    'redmi': r"C:\Users\vijayk\Desktop\project\project\Redmi A4 5G.csv",
    'mouse': r"C:\Users\vijayk\Desktop\project\project\mouse.csv",
}

# Product IDs from environment variables
PRODUCT_IDS = {
    'firebolt': os.getenv('FIREBOLT_PRODUCT_ID', '5898709734021221634'),
    'redmi': os.getenv('REDMI_PRODUCT_ID', '5898709734021221634'),
    'mouse': os.getenv('MOUSE_PRODUCT_ID', '5898709734021221634')
}

# Load sentiment analysis pipeline
pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

def fetch_product_prices(product_id):
    try:
        # Get API key from environment variables
        api_key = os.getenv('SERPAPI_KEY')
        
        if not api_key:
            print("Warning: SerpAPI key not found in environment variables")
            return get_fallback_prices()
        
        # Configure SerpAPI parameters for Indian region
        params = {
            "engine": "google_product",
            "product_id": product_id,
            "api_key": api_key,
            "gl": "in",  # Set region to India
            "hl": "en",  # Set language to English
            "location": "India"  # Specify location
        }
        
        # Make the API request
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "product_results" in results:
            product_data = results["product_results"]
            
            # Extract prices from different sellers
            prices = []
            
            # Add main product price
            if "price" in product_data:
                prices.append({
                    "price": product_data["price"],
                    "rating": product_data.get("rating", "N/A"),
                    "source": "google_shopping"
                })
            
            # Add prices from other sellers if available
            if "sellers" in product_data:
                for seller in product_data["sellers"][:2]:  # Get top 2 sellers
                    prices.append({
                        "price": seller.get("price", "N/A"),
                        "rating": seller.get("rating", "N/A"),
                        "source": seller.get("name", "unknown")
                    })
            
            return prices if prices else get_fallback_prices()
            
    except Exception as e:
        print(f"Error fetching prices: {str(e)}")
        return get_fallback_prices()
    
    return get_fallback_prices()

def get_fallback_prices():
    """Return fallback prices for different Indian retailers"""
    return [
        {
            "price": "₹4,999",
            "rating": "4.5",
            "source": "amazon.in"
        },
        {
            "price": "₹4,499",
            "rating": "4.3",
            "source": "flipkart"
        },
        {
            "price": "₹4,799",
            "rating": "4.4",
            "source": "croma"
        }
    ]

def load_and_analyze_data(product):
    # Load the dataset based on selected product
    file_path = PRODUCT_FILES.get(product)
    if not file_path:
        return None
    
    df = pd.read_csv(file_path)
    review_column = 'reviewTitle'
    
    # Clean and process the data
    df = df.dropna(subset=[review_column])
    df[['Sentiment', 'Confidence']] = pd.DataFrame(analyze_sentiment(df[review_column].tolist()), index=df.index)
    return df

def analyze_sentiment(reviews):
    results = pipe(reviews)
    return [(result['label'], result['score']) for result in results]

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/', methods=['GET'])
def home():
    selected_product = request.args.get('product')
    if not selected_product:
        return redirect(url_for('products'))
        
    df = load_and_analyze_data(selected_product)
    
    if df is None:
        return redirect(url_for('products'))

    # Fetch prices using SerpAPI
    product_id = PRODUCT_IDS.get(selected_product)
    prices = fetch_product_prices(product_id)
    
    # Calculate sentiment stats
    positive_reviews = df[df['Sentiment'] == 'POSITIVE']
    negative_reviews = df[df['Sentiment'] == 'NEGATIVE']
    
    pos_count = len(positive_reviews)
    neg_count = len(negative_reviews)
    total_reviews = len(df)
    
    # Calculate sentiment score (0-100)
    sentiment_score = int((pos_count / total_reviews) * 100) if total_reviews > 0 else 0
    
    # Extract product rating if available
    rating = 0
    if 'rating' in df.columns:
        df['rating_numeric'] = pd.to_numeric(df['rating'], errors='coerce')
        avg_rating = df['rating_numeric'].mean()
        rating = int((avg_rating / 5) * 100) if not pd.isna(avg_rating) else 0
    
    # Calculate total score
    rating_weight = 0.4
    sentiment_weight = 0.6
    total_score = int(rating * rating_weight + sentiment_score * sentiment_weight)
    
    # Get sample reviews
    pos_reviews = positive_reviews['reviewTitle'].tolist()[:5]
    neg_reviews = negative_reviews['reviewTitle'].tolist()[:5]
    
    pros = extract_features(pos_reviews)
    cons = extract_features(neg_reviews)
    summary = generate_summary(sentiment_score, pros, cons)
    
    # Prepare data for template with real prices
    results = {
        "shopping_results": [
            {
                "title": selected_product.title(),
                "price": price["price"],
                "rating": price["rating"],
                "source": price["source"],
                "thumbnail": "https://via.placeholder.com/300x300"
            } for price in prices
        ]
    }
    
    score_breakdown = {
        "rating_component": rating,
        "sentiment_component": sentiment_score,
        "rating_weight": rating_weight,
        "sentiment_weight": sentiment_weight
    }
    
    return render_template('index.html', 
                          results=results,
                          pros=pros,
                          cons=cons,
                          summary=summary,
                          total_score=total_score,
                          score_breakdown=score_breakdown,
                          selected_product=selected_product,
                          products=list(PRODUCT_FILES.keys()))

@app.route('/sentiment', methods=['GET'])
def get_sentiment():
    positive_reviews = df[df['Sentiment'] == 'POSITIVE'][review_column].tolist()
    negative_reviews = df[df['Sentiment'] == 'NEGATIVE'][review_column].tolist()
    
    response = {
        "positive_reviews": positive_reviews[:5],
        "negative_reviews": negative_reviews[:5],
    }
    return jsonify(response)

# Helper function to extract key features/aspects from reviews
def extract_features(reviews, max_features=5):
    # This is a simplified implementation
    # In a real application, you might use NLP techniques like named entity recognition,
    # keyword extraction, or topic modeling
    
    # Example implementation: Just take first few words of each review
    features = []
    for review in reviews:
        # Split review and take first 3 words
        words = review.split()
        if len(words) >= 3:
            feature = " ".join(words[:3])
            features.append(feature)
        
    # Return unique features, limited to max_features
    return list(set(features))[:max_features]

# Helper function to generate a summary based on sentiment analysis
def generate_summary(sentiment_score, pros, cons):
    if sentiment_score > 80:
        sentiment_desc = "overwhelmingly positive"
    elif sentiment_score > 60:
        sentiment_desc = "generally positive"
    elif sentiment_score > 40:
        sentiment_desc = "mixed"
    elif sentiment_score > 20:
        sentiment_desc = "generally negative"
    else:
        sentiment_desc = "overwhelmingly negative"
    
    summary = f"Based on our analysis, customer sentiment about this product is {sentiment_desc}. "
    
    if pros:
        summary += f"Customers particularly appreciate aspects like {', '.join(pros[:3])}. "
    
    if cons:
        summary += f"However, some users have concerns about {', '.join(cons[:3])}. "
    
    recommendation = ""
    if sentiment_score > 70:
        recommendation = "This product is highly recommended based on customer feedback."
    elif sentiment_score > 50:
        recommendation = "This product appears to be a solid choice, though it may not be perfect for everyone."
    elif sentiment_score > 30:
        recommendation = "Consider checking alternatives before purchasing this product."
    else:
        recommendation = "Based on customer sentiment, we suggest exploring other options."
    
    return summary + recommendation

if __name__ == '__main__':
    app.run(debug=True)