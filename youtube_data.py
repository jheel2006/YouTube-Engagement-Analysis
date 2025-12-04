import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import isodate

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Make sure it's in your .env file.")

# Categories with duration-specific search terms - OPTIMIZED FOR SHORT VIDEO DOMINANCE
CATEGORIES = {
    "20": {
        "name": "Gaming",
        "short_terms": ["gaming shorts", "gaming clip", "gaming clips short", "best gaming moments", "funny gaming short", "gaming fails short", "epic gaming short", "crazy gaming clip", "pro gameplay clip", "clutch moment", "minecraft short", "fortnite short", "valorant short", "roblox short", "gta short", "gaming meme short", "glitch moment", "viral gaming clip"],
        "long_terms": ["full gameplay", "gaming stream", "complete walkthrough", "game review", "let's play", "gaming tutorial"]
    },
    "10": {
        "name": "Music",
        "short_terms": ["music video", "song", "cover", "performance", "live performance", "music clip", "acoustic"],
        "long_terms": ["full album", "concert", "music documentary", "album review", "live concert", "music history"]
    },
    "26": {
        "name": "How-to & Style",
        "short_terms": ["makeup tips","hair tips","outfit ideas","style hacks","beauty hacks","quick makeup","quick hair","easy outfit","fashion hack","simple makeup","nail ideas","easy hairstyle","skincare tips","quick beauty","simple outfit","hair hack","makeup idea","style idea","closet tips","basic makeup"],
        "long_terms": ["full makeup tutorial", "hair transformation", "get ready with me", "fashion lookbook", "full beauty routine", "styling guide", "makeup collection", "wardrobe tour"]
    },
    # "22": {
    #     "name": "People & Blogs",
    #     "short_terms": ["vlog clip", "daily vlog", "story time", "update", "quick vlog", "life update", "behind the scenes"],
    #     "long_terms": ["full vlog", "day in my life", "life story", "long vlog", "weekly vlog", "detailed story"]
    # },
    # "24": {
    #     "name": "Entertainment",
    #     "short_terms": ["comedy sketch", "funny video", "comedy clip", "funny moments", "meme", "reaction", "prank"],
    #     "long_terms": ["movie review", "podcast", "talk show", "comedy special", "full episode", "interview"]
    # },
    "28": {
        "name": "Science & Technology",
        "short_terms": ["tech news", "gadget review", "tech tips", "new technology", "tech update", "device review", "tech explained"],
        "long_terms": ["tech documentary", "in-depth review", "tech tutorial", "technology explained", "full tech review", "tech analysis"]
    }
}

print("Loaded API key:", API_KEY[:5] + "*****")

# Parse ISO 8601 duration to seconds
def iso_to_seconds(duration):
    try:
        return int(isodate.parse_duration(duration).total_seconds())
    except:
        return None

# Fetch video IDs using search with duration filter
def get_video_ids_by_search(search_query, video_duration, max_videos=30):
    """
    Fetch videos using search query with duration filter
    video_duration: 'short' (<4min), 'medium' (4-20min), 'long' (>20min), 'any' (all)
    """
    video_ids = []
    next_page = None

    while len(video_ids) < max_videos:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "id",
            "type": "video",
            "q": search_query,
            "maxResults": min(50, max_videos - len(video_ids)),
            "order": "viewCount",
            "publishedAfter": "2024-01-01T00:00:00Z",
            "key": API_KEY
        }
        
        # Only add videoDuration if not 'any'
        if video_duration != 'any':
            params["videoDuration"] = video_duration
        
        if next_page:
            params["pageToken"] = next_page

        try:
            res = requests.get(url, params=params).json()
            
            if "error" in res:
                print(f"    API Error: {res['error'].get('message', 'Unknown error')}")
                break
                
            items = res.get("items", [])
            if not items:
                break

            for item in items:
                if "videoId" in item.get("id", {}):
                    video_ids.append(item["id"]["videoId"])

            next_page = res.get("nextPageToken")
            if not next_page or len(video_ids) >= max_videos:
                break

            time.sleep(0.3)
        except Exception as e:
            print(f"    Error fetching videos: {e}")
            break

    return list(set(video_ids))[:max_videos]  # Remove duplicates

# Fetch full video details
def get_video_details(video_ids, target_category_id, category_name):
    details = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": API_KEY
        }

        try:
            res = requests.get(url, params=params).json()
            
            if "error" in res:
                print(f"    API Error: {res['error'].get('message', 'Unknown error')}")
                continue
                
            for item in res.get("items", []):
                snippet = item.get("snippet", {})
                cat_id = snippet.get("categoryId")
                
                # Only include if it matches our target category
                if cat_id != target_category_id:
                    continue
                
                vid = item.get("id")
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                duration_sec = iso_to_seconds(content.get("duration", "PT0S"))
                if duration_sec is None or duration_sec == 0:
                    continue

                details.append({
                    "video_id": vid,
                    "title": snippet.get("title"),
                    "category": cat_id,
                    "category_name": category_name,
                    "duration_seconds": duration_sec,
                    "duration_minutes": duration_sec / 60,
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "published_at": snippet.get("publishedAt")
                })

            time.sleep(0.3)
        except Exception as e:
            print(f"    Error fetching details: {e}")
            continue

    return details

# Main execution
def main():
    all_short_videos = []
    all_long_videos = []

    # PHASE 1: Collect SHORT videos - exactly 30 per category (buffer for filtering)
    print(f"\n{'='*60}")
    print("PHASE 1: COLLECTING SHORT VIDEOS (<10 min)")
    print(f"Target: Exactly 30 short videos per category")
    print(f"{'='*60}")
    
    target_per_category = 30
    
    for cat_id, cat_info in CATEGORIES.items():
        cat_name = cat_info["name"]
        short_terms = cat_info["short_terms"]
        
        print(f"\n{cat_name}:")
        category_short = []
        
        # Keep looping through search terms until we get exactly 25
        attempts = 0
        max_attempts = 10  # Prevent infinite loops
        
        while len({v["video_id"]: v for v in category_short}.values()) < target_per_category and attempts < max_attempts:
            for search_term in short_terms:
                current_count = len({v["video_id"]: v for v in category_short}.values())
                if current_count >= target_per_category:
                    break
                    
                print(f"  '{search_term}'... (currently {current_count}/{target_per_category})", end=" ")
                # Increase fetch amount to get more videos
                video_ids = get_video_ids_by_search(search_term, "any", max_videos=80)
                
                if video_ids:
                    video_details = get_video_details(video_ids, cat_id, cat_name)
                    # Filter to short videos (1-10 min)
                    short_videos = [v for v in video_details if 1 <= v["duration_minutes"] < 10]
                    category_short.extend(short_videos)
                    new_count = len({v["video_id"]: v for v in category_short}.values())
                    print(f"✓ {new_count - current_count} new")
                else:
                    print("✗ None")
                    
                if len({v["video_id"]: v for v in category_short}.values()) >= target_per_category:
                    break
            
            attempts += 1
        
        # Remove duplicates and filter by duration BEFORE limiting
        unique_videos = {v["video_id"]: v for v in category_short}.values()
        # CRITICAL: Filter to correct duration range (1-10 min) AND remove shorts (<60s)
        valid_short = [v for v in unique_videos if 1 <= v["duration_minutes"] < 10 and v["duration_seconds"] > 60]
        
        # Take only the target number
        unique_short = list(valid_short)[:target_per_category]
        all_short_videos.extend(unique_short)
        
        if len(unique_short) < target_per_category:
            print(f"  ⚠️  Warning: Only got {len(unique_short)}/{target_per_category} VALID short videos for {cat_name}")
        else:
            print(f"  ✅ Total short for {cat_name}: {len(unique_short)}")
    
    print(f"\n{'='*60}")
    print(f"PHASE 1 COMPLETE: {len(all_short_videos)} SHORT VIDEOS COLLECTED")
    print(f"{'='*60}")
    
    # PHASE 2: Now collect LONG videos evenly across categories
    print(f"\n{'='*60}")
    print("PHASE 2: COLLECTING LONG VIDEOS (>20 min)")
    print(f"Target: 30 long videos per category")
    print(f"{'='*60}")
    
    target_per_category = 30
    
    for cat_id, cat_info in CATEGORIES.items():
        cat_name = cat_info["name"]
        long_terms = cat_info["long_terms"]
        
        print(f"\n{cat_name}:")
        category_long = []
        
        for search_term in long_terms:
            # Check if we have enough for this category
            current_count = len({v["video_id"]: v for v in category_long}.values())
            if current_count >= target_per_category:
                print(f"  (Already have {target_per_category} for this category)")
                break
                
            print(f"  '{search_term}'...", end=" ")
            
            video_ids = get_video_ids_by_search(search_term, "long", max_videos=30)
            
            if video_ids:
                video_details = get_video_details(video_ids, cat_id, cat_name)
                # Filter to long videos
                long_videos = [v for v in video_details if v["duration_minutes"] > 20]
                category_long.extend(long_videos)
                print(f"✓ {len(long_videos)} long")
            else:
                print("✗ None")
        
        # Remove duplicates and filter by duration BEFORE limiting
        unique_videos = {v["video_id"]: v for v in category_long}.values()
        # CRITICAL: Filter to correct duration range (>20 min) AND remove shorts (<60s)
        valid_long = [v for v in unique_videos if v["duration_minutes"] > 20 and v["duration_seconds"] > 60]
        
        # Take only the target number
        unique_long = list(valid_long)[:target_per_category]
        all_long_videos.extend(unique_long)
        
        if len(unique_long) < target_per_category:
            print(f"  ⚠️  Warning: Only got {len(unique_long)}/{target_per_category} VALID long videos for {cat_name}")
        else:
            print(f"  ✅ Total long for {cat_name}: {len(unique_long)}")
    
    print(f"\n{'='*60}")
    print(f"PHASE 2 COMPLETE: {len(all_long_videos)} LONG VIDEOS COLLECTED")
    print(f"{'='*60}")
    
    # Combine all data
    all_data = list(all_short_videos) + list(all_long_videos)

    if not all_data:
        print("\n❌ No data collected. Exiting.")
        return

    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    
    # NO MORE FILTERING - already filtered during collection!
    print(f"\nTotal videos collected: {len(df)}")
    
    print(f"\nCategory distribution:")
    print(df["category_name"].value_counts().to_string())
    
    # Calculate engagement metrics
    df["like_view_ratio"] = df.apply(
        lambda row: row["likes"] / row["views"] if row["views"] > 0 else 0,
        axis=1
    )
    df["comment_view_ratio"] = df.apply(
        lambda row: row["comments"] / row["views"] if row["views"] > 0 else 0,
        axis=1
    )
    # Combined engagement: (likes + comments) / views
    df["engagement_rate"] = df.apply(
        lambda row: (row["likes"] + row["comments"]) / row["views"] if row["views"] > 0 else 0,
        axis=1
    )
    
    # THEN split by duration
    short_df = df[df["duration_minutes"] < 10]
    long_df = df[df["duration_minutes"] > 20]
    
    print(f"\nDuration distribution:")
    print(f"  Short videos (<10 min): {len(short_df)}")
    print(f"  Long videos (>20 min): {len(long_df)}")
    
    # Show average engagement by duration
    print(f"\nAverage ENGAGEMENT by video length:")
    print(f"  Short (<10 min):")
    print(f"    Like rate: {short_df['like_view_ratio'].mean():.4f}")
    print(f"    Comment rate: {short_df['comment_view_ratio'].mean():.4f}")
    print(f"    Total engagement: {short_df['engagement_rate'].mean():.4f}")
    print(f"  Long (>20 min):")
    print(f"    Like rate: {long_df['like_view_ratio'].mean():.4f}")
    print(f"    Comment rate: {long_df['comment_view_ratio'].mean():.4f}")
    print(f"    Total engagement: {long_df['engagement_rate'].mean():.4f}")

    # Save CSV
    df.to_csv("youtube_length_engagement.csv", index=False)
    print(f"\n✓ Saved dataset as youtube_length_engagement.csv")
    print(f"✓ Total rows in dataset: {df.shape[0]}")

if __name__ == "__main__":
    main()