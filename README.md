# AI-Powered Product Review Analyzer

## Overview
This project is an AI-powered shopping assistant that helps users make informed purchase decisions by analyzing product reviews. It provides a summarized verdict on whether to buy a product based on sentiment analysis and key insights extracted from reviews.

## Features
- **Search for a Product**: Users can select the product they want to evaluate.
- **Sentiment Analysis**: Uses AI (DistilBERT) to analyze reviews and determine overall sentiment.
- **Pros and Cons Extraction**: Automatically extracts the key advantages and disadvantages of the product from reviews.
- **Final Verdict**: Provides a concise summary and recommendation on whether to buy the product.

## Tech Stack
- **Frontend**: HTML, CSS
- **Backend**: Python, Flask
- **AI Model**: DistilBERT (fine-tuned for sentiment analysis)
- **Database**: Optional (for storing past searches)
- **APIs**: Web scraping or integration with product review APIs (e.g., Amazon, Flipkart, BestBuy)

## System Architecture
 (https://github.com/user-attachments/assets/f9f5c03f-0315-4fe3-a736-4e170b0f32af)
The system follows a simple flow:
1. The user selects a product.
2. The backend fetches reviews from a database or external sources.
3. The AI model processes the reviews to determine sentiment and extract pros/cons.
4. The processed data is sent back to the frontend, displaying a final verdict.

## Installation & Setup
### Prerequisites
- Python 3.x
- Flask
- Transformers (Hugging Face library for DistilBERT)
- BeautifulSoup (for web scraping, if needed)
- HTML & CSS for frontend

### Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/ai-product-review-analyzer.git
   cd ai-product-review-analyzer
   ```
2. **Set up a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Flask Server:**
   ```bash
   python app.py
   ```
5. **Access the Web Interface:**
   Open `http://127.0.0.1:5000` in your browser.

## Usage
1. Enter the product name in the search bar.
2. The system fetches relevant reviews.
3. AI processes the reviews to generate a sentiment score.
4. A summarized verdict, pros, and cons are displayed.

## Future Enhancements
- **Comparison Feature**: Compare multiple products based on sentiment scores.
- **Price Tracking**: Monitor price changes and notify users of discounts.
- **Fake Review Detection**: Identify and filter out unreliable reviews.
- **Personalized Recommendations**: Suggest similar products based on user preferences.
  
## Limitations: 
Due to the time-consuming nature of API requests and web scraping, we opted to manually extract and load the datasets for faster processing.

## Contribution
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Added a new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a Pull Request.

## License
This project is open-source and available under the MIT License.

