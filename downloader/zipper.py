"""
Create ZIP archive of downloaded content.
"""

import zipfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ZipCreator:
    """Creates ZIP archive of downloaded content."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def create_backup_zip(self, output_name: str = "instagram_saved_backup.zip") -> Path:
        """
        Create a ZIP archive of all downloads.
        
        Args:
            output_name: Name of the output ZIP file
            
        Returns:
            Path to created ZIP file
        """
        zip_path = self.base_path.parent / output_name
        
        try:
            logger.info(f"Creating ZIP archive: {output_name}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from downloads directory
                for file_path in self.base_path.rglob('*'):
                    if file_path.is_file():
                        # Create relative path for archive
                        arcname = file_path.relative_to(self.base_path.parent)
                        zipf.write(file_path, arcname)
                        logger.debug(f"Added to ZIP: {arcname}")
            
            # Get file size
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            logger.info(f"ZIP archive created successfully: {zip_path.name} ({size_mb:.2f} MB)")
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating ZIP archive: {str(e)}")
            raise
    
    def create_metadata_only_zip(self, output_name: str = "instagram_metadata.zip") -> Path:
        """
        Create a ZIP archive of only metadata files.
        
        Args:
            output_name: Name of the output ZIP file
            
        Returns:
            Path to created ZIP file
        """
        zip_path = self.base_path.parent / output_name
        metadata_dir = self.base_path / "metadata"
        
        try:
            logger.info(f"Creating metadata ZIP: {output_name}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in metadata_dir.rglob('*.json'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.base_path.parent)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Metadata ZIP created: {zip_path.name}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating metadata ZIP: {str(e)}")
            raise
