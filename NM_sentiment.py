import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize VADER once
sid = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """
    Input  : review text (string)
    Output : 'positive', 'negative', or 'neutral'
    """

    # Handle missing / empty text safely
    if pd.isna(text) or str(text).strip() == "":
        return "neutral"

    text = str(text)

    score = sid.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"
