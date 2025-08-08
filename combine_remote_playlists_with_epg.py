import requests
from datetime import datetime
import re

# ===== CONFIGURATION =====
# Add or remove playlist URLs here as needed
PLAYLISTS = [
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/Backup.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/TheTVApp.m3u8",
    "https://raw.githubusercontent.com/BuddyChewChew/buddylive/refs/heads/main/en/videoall.m3u",
    "https://world-proxifier.xyz/streamed/playlist?timezone=et"
    # Add more playlists here in the format: "URL_TO_PLAYLIST"
]

# EPG URL
EPG_URL = "https://github.com/BuddyChewChew/My-Streams/raw/refs/heads/main/epgs/Backup-epg.xml.gz"

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
    
    # Create a dictionary to store groups and their channels
    groups = {}
    current_group = "Ungrouped"
    
    # First pass: organize channels by their groups
    i = 0
    while i < len(playlist_content):
        line = playlist_content[i]
        
        # Check if this is a group title line
        if line.startswith("#EXTGRP:"):
            current_group = line.split(':', 1)[1].strip()
            i += 1
            continue
            
        # Check if this is a channel info line
        if line.startswith("#EXTINF"):
            # Extract group-title if it exists
            group_match = re.search(r'group-title="([^"]*)"', line)
            if group_match:
                current_group = group_match.group(1).split(',')[0].strip() or "Ungrouped"
            
            # Get the channel URL (next line)
            if i + 1 < len(playlist_content) and not playlist_content[i+1].startswith('#'):
                channel_url = playlist_content[i+1]
                if current_group not in groups:
                    groups[current_group] = []
                groups[current_group].append((line, channel_url))
                i += 2
                continue
        
        i += 1
    
    # Write the playlist header
    outfile.write(f'#PLAYLIST:◻️ {source_name}\n')
    outfile.write(f'#EXTGRP:◻️ {source_name}\n\n')
    
    # Write groups and their channels
    for group, channels in groups.items():
        outfile.write(f'#GROUP:{group}\n')
        for channel_info, channel_url in channels:
            outfile.write(f'{channel_info}\n')
            outfile.write(f'{channel_url}\n')
        outfile.write('\n')
    
    outfile.write('\n' + '='*50 + '\n\n')  # Separator between playlists

def main():
    """Main function to combine playlists"""
    print(f"🚀 Starting to combine {len(PLAYLISTS)} playlists...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Write header with EPG URL and timestamp
        outfile.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')
        outfile.write(f'# Generated on {datetime.utcnow().isoformat()} UTC\n\n')
        
        # Process each playlist
        for url in PLAYLISTS:
            print(f"🔄 Processing: {url}")
            content = fetch_playlist(url)
            if content:
                source_name = get_playlist_name(url)
                process_playlist(content, source_name, outfile)
                print(f"✅ Added: {source_name} with groups")
    
    print(f"\n🎉 Success! Combined playlist saved as '{OUTPUT_FILE}'")
    print(f"📺 EPG URL: {EPG_URL}")

if __name__ == "__main__":
    main()
