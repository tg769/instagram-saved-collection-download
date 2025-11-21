"""
Instagram Saved Posts Downloader - GUI Application

Optional Tkinter-based graphical interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from downloader.client import InstagramClient
from downloader.fetch import SavedMediaFetcher
from downloader.download import MediaDownloader
from downloader.metadata import MetadataExtractor
from downloader.utils import DownloadTracker, ensure_directories
from downloader.zipper import ZipCreator


class InstagramDownloaderGUI:
    """GUI application for Instagram saved posts downloader."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Saved Posts Downloader")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Setup paths
        self.base_dir = Path(__file__).parent.parent
        self.downloads_dir = self.base_dir / "downloads"
        self.data_dir = self.base_dir / "data"
        
        # Variables
        self.is_downloading = False
        self.collections = {}
        self.ig_client = None
        self.fetcher = None
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create and layout GUI widgets."""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="📸 Instagram Saved Posts Downloader",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # Session ID input
        input_frame = ttk.LabelFrame(self.root, text="Authentication", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Session ID:").pack(anchor=tk.W)
        
        self.session_entry = ttk.Entry(input_frame, width=60, show="*")
        self.session_entry.pack(fill=tk.X, pady=5)
        
        # Instructions
        instructions = (
            "How to get your session ID:\n"
            "1. Open Instagram in browser and log in\n"
            "2. Press F12 → Application → Cookies → instagram.com\n"
            "3. Copy the 'sessionid' value"
        )
        instruction_label = ttk.Label(input_frame, text=instructions, foreground="gray")
        instruction_label.pack(anchor=tk.W, pady=5)
        
        # Login button
        login_btn_frame = ttk.Frame(input_frame)
        login_btn_frame.pack(fill=tk.X, pady=5)
        
        self.login_btn = ttk.Button(
            login_btn_frame,
            text="🔐 Login & Fetch Collections",
            command=self.fetch_collections
        )
        self.login_btn.pack(side=tk.LEFT)
        
        # Collection selection
        collection_frame = ttk.LabelFrame(self.root, text="Collection Selection", padding="10")
        collection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(collection_frame, text="Select Collection:").pack(anchor=tk.W)
        
        self.collection_var = tk.StringVar()
        self.collection_combo = ttk.Combobox(
            collection_frame,
            textvariable=self.collection_var,
            state="disabled",
            width=57
        )
        self.collection_combo.pack(fill=tk.X, pady=5)
        
        ttk.Label(collection_frame, text="Number of Posts (leave empty for all):").pack(anchor=tk.W, pady=(10, 0))
        
        self.amount_entry = ttk.Entry(collection_frame, width=20)
        self.amount_entry.pack(anchor=tk.W, pady=5)
        self.amount_entry.insert(0, "")
        
        # Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(
            button_frame,
            text="⬇️  Download Selected Collection",
            command=self.start_download,
            state=tk.DISABLED
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️  Stop",
            command=self.stop_download,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📁 Open Downloads Folder",
            command=self.open_downloads_folder
        ).pack(side=tk.LEFT, padx=5)
        
        # Progress
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to download")
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Log output
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def log(self, message):
        """Add message to log text widget."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status label."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, current, total):
        """Update progress bar."""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
        self.root.update_idletasks()
    
    def fetch_collections(self):
        """Fetch collections from Instagram."""
        sessionid = self.session_entry.get().strip()
        
        if not sessionid:
            messagebox.showerror("Error", "Please enter your Instagram session ID")
            return
        
        # Disable login button
        self.login_btn.config(state=tk.DISABLED)
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start fetch in thread
        thread = threading.Thread(target=self.fetch_collections_worker, args=(sessionid,))
        thread.daemon = True
        thread.start()
    
    def fetch_collections_worker(self, sessionid):
        """Worker function to fetch collections."""
        try:
            # Login
            self.log("🔐 Logging in to Instagram...")
            self.update_status("Logging in...")
            
            self.ig_client = InstagramClient()
            if not self.ig_client.login_with_session(sessionid):
                self.log("❌ Login failed! Please check your session ID.")
                messagebox.showerror("Login Failed", "Invalid session ID or login failed")
                self.root.after(0, lambda: self.login_btn.config(state=tk.NORMAL))
                return
            
            username = self.ig_client.get_username()
            self.log(f"✅ Successfully logged in as @{username}")
            
            # Fetch collections
            self.log("📂 Fetching your collections...")
            self.update_status("Fetching collections...")
            
            self.fetcher = SavedMediaFetcher(self.ig_client.get_client())
            self.collections = self.fetcher.get_collections()
            
            if not self.collections:
                self.log("⚠️  No collections found")
                messagebox.showwarning("No Collections", "No collections found in your account")
                self.root.after(0, lambda: self.login_btn.config(state=tk.NORMAL))
                return
            
            self.log(f"✅ Found {len(self.collections)} collections")
            
            # Update UI with collections
            self.root.after(0, self.populate_collections)
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            self.root.after(0, lambda: self.login_btn.config(state=tk.NORMAL))
    
    def populate_collections(self):
        """Populate the collection dropdown with fetched collections."""
        collection_names = []
        
        # Add "All Saved Posts" option
        collection_names.append("All Saved Posts (download everything)")
        
        # Add other collections
        for col in self.collections:
            name = col.get('name', 'Unnamed')
            count = col.get('count', 0)
            collection_names.append(f"{name} ({count} posts)")
        
        self.collection_combo['values'] = collection_names
        self.collection_combo.current(0)  # Select first option by default
        self.collection_combo.config(state="readonly")
        
        # Enable download button
        self.download_btn.config(state=tk.NORMAL)
        
        self.log("\n📌 Select a collection and click Download\n")
        self.update_status("Ready to download")
    
    def start_download(self):
        """Start the download process in a separate thread."""
        if not self.ig_client or not self.fetcher:
            messagebox.showerror("Error", "Please login and fetch collections first")
            return
        
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        # Get selected collection
        selected_index = self.collection_combo.current()
        if selected_index < 0:
            messagebox.showerror("Error", "Please select a collection")
            return
        
        # Determine collection ID
        if selected_index == 0:
            collection_id = None  # All saved posts
            collection_name = "All Saved Posts"
        else:
            collection_id = self.collections[selected_index - 1].get('id')
            collection_name = self.collections[selected_index - 1].get('name')
        
        # Get amount
        amount_text = self.amount_entry.get().strip()
        try:
            amount = int(amount_text) if amount_text else 0
            if amount < 0:
                messagebox.showerror("Error", "Amount must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for amount")
            return
        
        # Disable download button, enable stop button
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_downloading = True
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start download in thread
        thread = threading.Thread(target=self.download_worker, args=(collection_id, collection_name, amount))
        thread.daemon = True
        thread.start()
    
    def stop_download(self):
        """Stop the download process."""
        self.is_downloading = False
        self.log("⚠️  Download stopped by user")
        self.update_status("Download stopped")
        self.download_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def download_worker(self, collection_id, collection_name, amount):
        """Worker function to handle the download process."""
        try:
            # Ensure directories
            ensure_directories(self.downloads_dir)
            self.data_dir.mkdir(exist_ok=True)
            
            # Initialize tracker
            tracker = DownloadTracker(self.data_dir)
            
            # Fetch saved posts from selected collection
            self.log(f"📥 Fetching posts from '{collection_name}'...")
            if amount > 0:
                self.log(f"   Limit: {amount} posts")
            self.update_status(f"Fetching posts from {collection_name}...")
            
            if collection_id is None:
                # Fetch all saved posts
                saved_medias = self.fetcher.fetch_all_saved_medias()
            else:
                # Fetch from specific collection
                saved_medias = self.fetcher.fetch_collection_medias(collection_id, amount)
            
            if not saved_medias:
                self.log("⚠️  No saved posts found")
                messagebox.showinfo("No Posts", "No saved posts found in your account")
                self.stop_download()
                return
            
            self.log(f"✅ Found {len(saved_medias)} saved posts")
            
            # Filter already downloaded
            to_download = [media for media in saved_medias if not tracker.is_downloaded(str(media.pk))]
            already_downloaded = len(saved_medias) - len(to_download)
            
            if already_downloaded > 0:
                self.log(f"ℹ️  {already_downloaded} posts already downloaded (skipping)")
            
            if not to_download:
                self.log("✅ All saved posts are already downloaded!")
                self.update_status("All posts already downloaded")
                
                # Create ZIP anyway
                self.log("📦 Creating ZIP backup...")
                zipper = ZipCreator(self.downloads_dir)
                zip_path = zipper.create_backup_zip()
                self.log(f"✅ ZIP created: {zip_path.name}")
                
                messagebox.showinfo("Complete", "All posts already downloaded!\nZIP backup created.")
                self.stop_download()
                return
            
            self.log(f"\n⬇️  Downloading {len(to_download)} new posts from '{collection_name}'...\n")
            self.update_status(f"Downloading {len(to_download)} posts...")
            
            # Initialize downloader
            downloader = MediaDownloader(self.ig_client.get_client(), self.downloads_dir)
            metadata_extractor = MetadataExtractor(self.downloads_dir / "metadata")
            
            # Download statistics
            successful = 0
            failed = 0
            
            # Download each post
            for idx, media in enumerate(to_download, 1):
                if not self.is_downloading:
                    self.log("⚠️  Download cancelled by user")
                    break
                
                pk = str(media.pk)
                media_type_name = downloader.get_media_type_name(media.media_type)
                username_post = media.user.username if media.user else "unknown"
                
                self.update_status(f"Downloading {idx}/{len(to_download)}: {media_type_name} from @{username_post}")
                self.update_progress(idx, len(to_download))
                
                try:
                    download_path = downloader.download_media(media)
                    
                    if download_path:
                        metadata_extractor.save_metadata(media, pk)
                        tracker.mark_downloaded(pk)
                        successful += 1
                        self.log(f"✅ [{idx}/{len(to_download)}] {media_type_name} from @{username_post}")
                    else:
                        failed += 1
                        self.log(f"❌ [{idx}/{len(to_download)}] Failed: {media_type_name} from @{username_post}")
                
                except Exception as e:
                    failed += 1
                    self.log(f"❌ [{idx}/{len(to_download)}] Error: {str(e)}")
            
            # Save tracker
            tracker.save_tracker()
            
            # Summary
            self.log("\n" + "="*50)
            self.log("📊 Download Summary")
            self.log("="*50)
            self.log(f"✅ Successfully downloaded: {successful}")
            self.log(f"❌ Failed: {failed}")
            self.log(f"📁 Total saved posts: {len(saved_medias)}")
            self.log("="*50)
            
            # Create ZIP
            if successful > 0:
                self.log("\n📦 Creating ZIP backup...")
                self.update_status("Creating ZIP backup...")
                
                try:
                    zipper = ZipCreator(self.downloads_dir)
                    zip_path = zipper.create_backup_zip()
                    self.log(f"✅ ZIP backup created: {zip_path.name}")
                except Exception as e:
                    self.log(f"❌ Failed to create ZIP: {str(e)}")
            
            self.log("\n🎉 Download complete!")
            self.update_status(f"Complete! Downloaded {successful} posts")
            
            messagebox.showinfo(
                "Download Complete",
                f"Successfully downloaded {successful} posts!\n"
                f"Failed: {failed}\n\n"
                f"Files saved to: {self.downloads_dir}"
            )
        
        except Exception as e:
            self.log(f"\n❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.is_downloading = False
    
    def open_downloads_folder(self):
        """Open the downloads folder in file explorer."""
        import os
        import platform
        
        if not self.downloads_dir.exists():
            messagebox.showwarning("Not Found", "Downloads folder doesn't exist yet")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(self.downloads_dir)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{self.downloads_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.downloads_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = InstagramDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
