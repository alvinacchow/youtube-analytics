import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def get_cat_map(cat_path):
    """Return a dictionary mapping category_id → category name"""
    with open(cat_path) as f:
        cat_dict = json.load(f)['items']
    return {int(item['id']): item['snippet']['title'] for item in cat_dict}

def load_and_clean(csv_path, cat_path, country=None, encoding='utf-8'):
    """Load the CSV and JSON, clean data, and return a ready-to-use DataFrame"""
    df = pd.read_csv(csv_path, encoding=encoding)
    
    # Convert date columns to datetime
    df['publish_time'] = pd.to_datetime(df['publish_time'])
    df['trending_date'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m')
    
    # Map category IDs to names
    cat_map = get_cat_map(cat_path)
    df['category'] = df['category_id'].map(cat_map)
    
    # Convert numeric columns to proper types
    numeric_cols = ['views', 'likes', 'dislikes', 'comment_count']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Compute derived columns
    df['engagement_rate'] = (df['likes'] + df['comment_count']) / df['views']
    df['publish_hour'] = df['publish_time'].dt.hour
    df['publish_day'] = df['publish_time'].dt.day_name()
    
    # Remove duplicate videos, keeping the latest trending record
    df = df.sort_values('trending_date', ascending=False) \
           .drop_duplicates(subset='video_id', keep='first')
    
    if country:
        df['country'] = country

    return df


def load_country(country_code: str, encoding=None):
    return load_and_clean(
        csv_path=DATA_DIR / f"{country_code}videos.csv",
        cat_path=DATA_DIR / f"{country_code}_category_id.json",
        country=country_code,
        encoding=encoding
    )