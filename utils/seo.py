def generate_high_rpm_seo(title, description, tags):
    geo_keywords = ["USA", "UK", "Canada", "North America", "English"]
    # Add geo keywords to tags if not present
    for kw in geo_keywords:
        if kw.lower() not in [t.lower() for t in tags]:
            tags.append(kw)
    # Add geo phrase to description
    desc_suffix = "\n\n🔥 This video is popular in USA, UK, Canada and worldwide!"
    description += desc_suffix
    # Add to title if not already
    if not any(kw in title for kw in geo_keywords):
        title += " | USA UK Canada"
    # Add hashtags
    hashtags = "#USA #UK #Canada #Trending #Viral"
    description += f"\n\n{hashtags}"
    return title, description, tags
