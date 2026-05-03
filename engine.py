from textblob import TextBlob

def analyze_sentiment(report_text):
    analysis = TextBlob(report_text)
    # Sentiment ranges from -1 (bad/urgent) to 1 (good)
    sentiment = analysis.sentiment.polarity
    
    # Urgent keywords
    urgent_keywords = ['leak', 'broken', 'waste', 'emergency', 'danger', 'burst', 'on']
    keyword_score = sum(2 for word in urgent_keywords if word in report_text.lower())
    
    # Calculate final score (scale of 0-10)
    priority_score = (1 - sentiment) + keyword_score
    return round(min(priority_score, 10), 2)

def get_category(text):
    text = text.lower()
    if any(word in text for word in ['light', 'ac', 'electricity', 'power']):
        return "Energy"
    if any(word in text for word in ['water', 'tap', 'leak', 'pipe']):
        return "Water"
    if any(word in text for word in ['food', 'mess', 'leftover']):
        return "Food Waste"
    return "General"
