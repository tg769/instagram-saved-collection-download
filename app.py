"""
Instagram Saved Posts Downloader - Main CLI Application

This application downloads all saved Instagram posts from your account.
"""

import sys
import logging
from pathlib import Path

# Check Python version
if sys.version_info < (3, 11) or sys.version_info >= (3, 14):
    print("\n⚠️  Python Version Warning")
    print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")
    print("This app works best with Python 3.11-3.13")
    if sys.version_info >= (3, 14):
        print("\n💡 Try running with Python 3.13:")
        print("   py -3.13 app.py")
        print("\nContinuing anyway, but may encounter errors...")
        print()

from tqdm import tqdm

from downloader.client import InstagramClient
from downloader.fetch import SavedMediaFetcher
from downloader.download import MediaDownloader
from downloader.metadata import MetadataExtractor
from downloader.utils import DownloadTracker, ensure_directories, get_timestamp
from downloader.zipper import ZipCreator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_downloader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   Instagram Saved Posts Downloader                        ║
    ║   Download all your saved Instagram posts                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_session_id() -> str:
    """Prompt user for Instagram session ID."""
    print("\n📋 To get your session ID:")
    print("   1. Open Instagram in your browser and log in")
    print("   2. Press F12 to open Developer Tools")
    print("   3. Go to Application > Cookies > instagram.com")
    print("   4. Find 'sessionid' and copy its value\n")
    
    sessionid = input("🔑 Paste your Instagram sessionid: ").strip()
    
    if not sessionid:
        print("❌ Session ID cannot be empty!")
        sys.exit(1)
    
    return sessionid


def select_collection(fetcher):
    """Let user select which collection(s) to download."""
    print("\n📂 Fetching your collections...")
    collections = fetcher.get_collections()
    
    if not collections:
        print("⚠️  No collections found. Using all saved posts.")
        return None, 0
    
    print("\n" + "="*60)
    print("Your Instagram Collections:")
    print("="*60)
    print(f"  0. All Saved Posts (download everything)")
    
    for idx, col in enumerate(collections, 1):
        name = col.get('name', 'Unnamed')
        count = col.get('count', 0)
        print(f"  {idx}. {name} ({count} posts)")
    
    print("="*60)
    
    # Get user choice
    while True:
        try:
            choice = input("\n📌 Select collection number (0 for all): ").strip()
            choice_num = int(choice)
            
            if choice_num < 0 or choice_num > len(collections):
                print(f"❌ Invalid choice. Please enter 0-{len(collections)}")
                continue
            
            # Get amount to download
            if choice_num == 0:
                collection_id = None
                collection_name = "All Saved Posts"
            else:
                selected = collections[choice_num - 1]
                collection_id = selected.get('id')
                collection_name = selected.get('name')
            
            # Ask how many posts
            print(f"\n📊 Selected: {collection_name}")
            amount_input = input("How many posts to download? (Enter for all, or a number): ").strip()
            
            if amount_input:
                amount = int(amount_input)
                if amount <= 0:
                    print("❌ Amount must be positive. Using all posts.")
                    amount = 0
            else:
                amount = 0
            
            return collection_id, amount
            
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def main():
    """Main application entry point."""
    print_banner()
    
    # Setup paths
    base_dir = Path(__file__).parent
    downloads_dir = base_dir / "downloads"
    data_dir = base_dir / "data"
    metadata_dir = downloads_dir / "metadata"
    
    # Ensure directories exist
    ensure_directories(downloads_dir)
    data_dir.mkdir(exist_ok=True)
    
    # Initialize components
    tracker = DownloadTracker(data_dir)
    
    # Get session ID from user
    sessionid = get_session_id()
    
    # Login to Instagram
    print("\n🔐 Logging in to Instagram...")
    ig_client = InstagramClient()
    
    if not ig_client.login_with_session(sessionid):
        print("❌ Login failed! Please check your session ID and try again.")
        sys.exit(1)
    
    username = ig_client.get_username()
    print(f"✅ Successfully logged in as @{username}")
    
    # Let user select collection
    fetcher = SavedMediaFetcher(ig_client.get_client())
    collection_id, amount = select_collection(fetcher)
    
    # Fetch posts based on selection
    if collection_id is None:
        print("\n📥 Fetching all saved posts...")
        saved_medias = fetcher.fetch_all_saved_medias()
    else:
        print(f"\n📥 Fetching posts from selected collection...")
        saved_medias = fetcher.fetch_collection_medias(collection_id, amount)
    
    if not saved_medias:
        print("⚠️  No posts found or unable to fetch posts.")
        return
    
    print(f"✅ Found {len(saved_medias)} posts.")
    
    # Filter out already downloaded posts
    to_download = [media for media in saved_medias if not tracker.is_downloaded(str(media.pk))]
    already_downloaded = len(saved_medias) - len(to_download)
    
    if already_downloaded > 0:
        print(f"ℹ️  {already_downloaded} posts already downloaded (skipping)")
    
    if not to_download:
        print("✅ All saved posts are already downloaded!")
        create_zip = input("\n📦 Create ZIP backup anyway? (y/n): ").lower().strip() == 'y'
        if create_zip:
            zipper = ZipCreator(downloads_dir)
            zip_path = zipper.create_backup_zip()
            print(f"✅ ZIP backup created: {zip_path}")
        return
    
    print(f"\n⬇️  Downloading {len(to_download)} new posts...\n")
    
    # Initialize downloader and metadata extractor
    downloader = MediaDownloader(ig_client.get_client(), downloads_dir)
    metadata_extractor = MetadataExtractor(metadata_dir)
    
    # Download statistics
    successful = 0
    failed = 0
    
    # Download each post with progress bar
    with tqdm(total=len(to_download), desc="Downloading", unit="post") as pbar:
        for media in to_download:
            pk = str(media.pk)
            media_type_name = downloader.get_media_type_name(media.media_type)
            username_post = media.user.username if media.user else "unknown"
            
            pbar.set_description(f"Downloading {media_type_name} from @{username_post}")
            
            try:
                # Download the media
                download_path = downloader.download_media(media)
                
                if download_path:
                    # Save metadata
                    metadata_extractor.save_metadata(media, pk)
                    
                    # Mark as downloaded
                    tracker.mark_downloaded(pk)
                    successful += 1
                else:
                    failed += 1
                    logger.warning(f"Failed to download pk {pk}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Error downloading pk {pk}: {str(e)}")
            
            pbar.update(1)
    
    # Save tracker
    tracker.save_tracker()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Download Summary")
    print("="*60)
    print(f"✅ Successfully downloaded: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total saved posts: {len(saved_medias)}")
    print("="*60)
    
    # Create ZIP backup
    print("\n📦 Creating ZIP backup...")
    try:
        zipper = ZipCreator(downloads_dir)
        zip_path = zipper.create_backup_zip()
        print(f"✅ ZIP backup created: {zip_path}")
    except Exception as e:
        logger.error(f"Failed to create ZIP backup: {str(e)}")
        print(f"❌ Failed to create ZIP backup: {str(e)}")
    
    print("\n🎉 Download complete!")
    print(f"📂 Downloads saved to: {downloads_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ An error occurred: {str(e)}")
        sys.exit(1)
