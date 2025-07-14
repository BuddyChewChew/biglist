import requests
from datetime import datetime
import re

# ===== CONFIGURATION =====
# Add or remove playlist URLs here as needed
PLAYLISTS = [
    "https://tinyurl.com/drewall8",
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/TheTVApp.m3u8",
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/Backup.m3u"
    # Add more playlists here in the format: "URL_TO_PLAYLIST"
]

# EPG URL
EPG_URL = "https://tvpass.org/epg.xml"

# Output file
OUTPUT_FILE = "combined_playlist.m3u"

# ===== FUNCTIONS =====
def get_playlist_name(url):
    """Extract a clean name from the playlist URL"""
    # Get the last part of URL and remove file extensions
    name = url.split('/')[-1]
    return re.sub(r'(\.m3u8?|\.txt)?$', '', name, flags=re.IGNORECASE).strip() or 'Unnamed_Playlist'

def fetch_playlist(url):
    """Fetch playlist content from URL"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def process_playlist(playlist_content, source_name, outfile):
    """Process and write playlist content to output file"""
    if not playlist_content:
        return
        
    # Add source group title
    outfile.write(f'# 📺 Source: {source_name}\n')
    outfile.write(f'#EXTGRP:{source_name}\n')
    
    for line in playlist_content:
        if line.startswith("#EXTINF"):
            # Add or update group-title
            if 'group-title=' not in line:
                line = line.replace("#EXTINF", f"#EXTINF group-title=\"{source_name}\"")
            elif 'group-title=""' in line:
                line = line.replace('group-title=""', f'group-title="{source_name}"')
            else:
                # Preserve existing group-title but add source as a secondary group
                line = line.replace('group-title="', f'group-title="{source_name}, ')
        
        if not line.startswith("#EXTM3U"):  # Skip the initial header
            outfile.write(line + "\n")
    
    outfile.write("\n")  # Space between sources

def main():
    """Main function to combine playlists"""
    print(f"🚀 Starting to combine {len(PLAYLISTS)} playlists...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Write header with EPG URL and timestamp
        outfile.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n\n')
        outfile.write(f'# Generated on {datetime.utcnow().isoformat()} UTC\n\n')
        
        # Process each playlist
        for url in PLAYLISTS:
            print(f"🔄 Processing: {url}")
            content = fetch_playlist(url)
            if content:
                source_name = get_playlist_name(url)
                process_playlist(content, source_name, outfile)
                print(f"✅ Added: {source_name}")
    
    print(f"\n🎉 Success! Combined playlist saved as '{OUTPUT_FILE}'")
    print(f"📺 EPG URL: {EPG_URL}")

if __name__ == "__main__":
    main()
