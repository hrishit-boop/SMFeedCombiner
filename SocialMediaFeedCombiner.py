import os
import requests
import tweepy
from datetime import datetime
from dotenv import load_dotenv


def load_credentials():
    # Load credentials from .env file
    load_dotenv()
    twitter_consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    twitter_consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    return (
        twitter_consumer_key,
        twitter_consumer_secret,
        twitter_access_token,
        twitter_access_token_secret,
        instagram_access_token,
    )


def fetch_twitter_feed(consumer_key, consumer_secret, access_token, access_token_secret, count=20):
    """
    Fetches the latest tweets from the authenticated user's home timeline.
    """
    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    api = tweepy.API(auth)
    tweets = api.home_timeline(count=count, tweet_mode='extended')
    result = []
    for tweet in tweets:
        result.append({
            'platform': 'X',
            'id': tweet.id_str,
            'text': tweet.full_text,
            'user': tweet.user.screen_name,
            'timestamp': tweet.created_at,
        })
    return result


def fetch_instagram_feed(access_token, limit=20):
    """
    Fetches the latest media posts from the authenticated Instagram user via the Basic Display API.
    """
    url = (
        f"https://graph.instagram.com/me/media"
        f"?fields=id,caption,media_url,timestamp"
        f"&access_token={access_token}"
        f"&limit={limit}"
    )
    resp = requests.get(url)
    data = resp.json()
    result = []
    for item in data.get('data', []):
        # Parse ISO timestamp to datetime
        ts = item['timestamp'].replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(ts)
        result.append({
            'platform': 'Instagram',
            'id': item['id'],
            'text': item.get('caption', ''),
            'media_url': item.get('media_url'),
            'timestamp': timestamp,
        })
    return result


def aggregate_feeds(twitter_items, instagram_items):
    """
    Combine and sort feeds from both platforms by timestamp (newest first).
    """
    combined = twitter_items + instagram_items
    combined.sort(key=lambda x: x['timestamp'], reverse=True)
    return combined


def main():
    # Load API credentials
    (
        ck,
        cs,
        at,
        ats,
        ig_token,
    ) = load_credentials()

    # Fetch feeds
    twitter_feed = fetch_twitter_feed(ck, cs, at, ats)
    instagram_feed = fetch_instagram_feed(ig_token)

    # Aggregate and display
    combined_feed = aggregate_feeds(twitter_feed, instagram_feed)
    for item in combined_feed:
        ts = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        header = f"[{item['platform']}] {ts}"
        if item['platform'] == 'X':
            print(f"{header} @{item['user']}: {item['text']}")
        else:
            print(f"{header} Instagram Post: {item['text']}")
            print(f"Media URL: {item['media_url']}")
        print('-' * 80)


if __name__ == "__main__":
    main()

# Instructions:
# 1. Install dependencies: `pip install tweepy requests python-dotenv`
# 2. Create a `.env` file with the following variables:
#    TWITTER_CONSUMER_KEY=...
#    TWITTER_CONSUMER_SECRET=...
#    TWITTER_ACCESS_TOKEN=...
#    TWITTER_ACCESS_TOKEN_SECRET=...
#    INSTAGRAM_ACCESS_TOKEN=...
# 3. Run: `python feed_aggregator.py` to see your combined feed.
