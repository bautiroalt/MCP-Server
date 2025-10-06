"""
File Manager for FastMCP Server.

This module provides a robust file management system that supports:
- File upload, download, and metadata management
- File versioning and history
- File system monitoring
- Asynchronous file operations
- Integration with context manager
"""

import asyncio
import hashlib
import json
import logging
import os
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Set, Tuple, Union, AsyncGenerator

import aiofiles
import aiofiles.os
import aiofiles.os as aios
from fastapi import UploadFile
from pydantic import BaseModel, Field, validator

from app.core.context_manager import ContextManager
from app.models.pydantic_models import Event, EventType

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB max file size
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json', 'yaml', 'yml',
    'xlsx', 'xls', 'xlsm', 'xlsb',  # Excel formats
    'doc', 'docx',  # Word formats
    'ppt', 'pptx',  # PowerPoint formats
    'zip', 'rar',   # Archive formats
    'py', 'js', 'html', 'css', 'md'  # Code and markup formats
}

class FileMetadata(BaseModel):
    """Metadata model for files."""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="File MIME type")
    size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="SHA-256 checksum")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
    updated_at: float = Field(default_factory=time.time, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    version: int = Field(1, description="File version number")
    tags: List[str] = Field(default_factory=list, description="File tags")
    is_deleted: bool = Field(False, description="Whether the file is marked as deleted")

class FileManager:
    """
    Manages file storage, retrieval, and versioning.
    
    Features:
    - Async file operations
    - File versioning
    - Metadata management
    - File system monitoring
    - Integration with context manager
    """
    
    def __init__(
        self,
        storage_root: str = "data/files",
        max_file_size: int = MAX_FILE_SIZE,
        allowed_extensions: Set[str] = None,
        context_manager: Optional[ContextManager] = None
    ):
        """
        Initialize the File Manager.
        
        Args:
            storage_root: Base directory for file storage
            max_file_size: Maximum allowed file size in bytes
            allowed_extensions: Set of allowed file extensions
            context_manager: Optional ContextManager instance for event publishing
        """
        self.storage_root = Path(storage_root)
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
        self.context_manager = context_manager or ContextManager()
        self._file_locks: Dict[str, asyncio.Lock] = {}
        self._setup_directories()
        
    def _setup_directories(self):
        """Ensure required directories exist."""
        self.storage_root.mkdir(parents=True, exist_ok=True)
        (self.storage_root / "tmp").mkdir(exist_ok=True)
        (self.storage_root / "versions").mkdir(exist_ok=True)
        
    def _get_file_path(self, file_id: str, version: int = None) -> Path:
        """Get the filesystem path for a file ID and optional version."""
        if version:
            return self.storage_root / "versions" / file_id / f"v{version}"
        return self.storage_root / file_id
        
    def _validate_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
        
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
        
    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish a file event to the context manager."""
        logger.info(f"Attempting to publish file event: {event_type} with data: {data}")
        if not self.context_manager:
            logger.warning("Context manager not available, skipping event publishing.")
            return
            
        try:
            event = Event(
                event_type=EventType.FILE_EVENT,
                source="file_manager",
                data={
                    "event": event_type,
                    "timestamp": time.time(),
                    **data
                },
                correlation_id=str(uuid.uuid4())
            )
            logger.debug(f"Created event object: {event.model_dump_json()}")
            await self.context_manager.publish_event(event)
            logger.info(f"Successfully published file event: {event_type}")
        except Exception as e:
            logger.error(f"Error publishing file event {event_type}: {e}", exc_info=True)
        
    async def upload_file(
        self,
        file: UploadFile,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> FileMetadata:
        """
        Upload a new file or new version of an existing file.
        
        Args:
            file: FastAPI UploadFile object
            metadata: Optional file metadata
            tags: Optional list of tags
            overwrite: Whether to overwrite existing file
            
        Returns:
            FileMetadata for the uploaded file
            
        Raises:
            ValueError: For invalid file or metadata
            IOError: For file system errors
        """
        # Validate input
        if not file.filename:
            raise ValueError("No filename provided")
            
        if not self._validate_extension(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
            
        # Generate file ID
        file_id = str(uuid.uuid4())
        temp_path = self.storage_root / "tmp" / f"upload_{file_id}"
        
        try:
            # Save file to temp location
            file_size = 0
            async with aiofiles.open(temp_path, "wb") as f:
                while content := await file.read(8192):
                    file_size += len(content)
                    if file_size > self.max_file_size:
                        raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
                    await f.write(content)
                    
            # Calculate checksum
            checksum = await self._calculate_checksum(temp_path)
            
            # Check for existing file with same content
            existing_file = await self._find_file_by_checksum(checksum)
            if existing_file and not overwrite:
                await aios.remove(temp_path)
                return existing_file
                
            # Check for existing file with same name
            existing_files = await self.list_files()
            existing_file = next((f for f in existing_files if f.filename == file.filename), None)
            
            if existing_file and not overwrite:
                # Get next version number
                versions = await self.get_file_versions(existing_file.file_id)
                next_version = max([v.version for v in versions], default=0) + 1
                
                # Move to version location
                version_path = self._get_file_path(existing_file.file_id, next_version)
                version_path.parent.mkdir(parents=True, exist_ok=True)
                await aios.rename(temp_path, version_path)
                
                # Create metadata for new version
                file_metadata = FileMetadata(
                    file_id=existing_file.file_id,
                    filename=file.filename,
                    content_type=file.content_type or "application/octet-stream",
                    size=file_size,
                    checksum=checksum,
                    metadata=metadata or {},
                    tags=tags or [],
                    created_at=time.time(),
                    updated_at=time.time(),
                    version=next_version
                )
                
                # Save metadata
                await self._save_metadata(file_metadata)
                
                # Publish event
                await self._publish_event("file_version_created", {
                    "file_id": existing_file.file_id,
                    "filename": file.filename,
                    "version": next_version,
                    "size": file_size
                })
                
                return file_metadata
                
            # Move to final location for new file
            final_path = self._get_file_path(file_id)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            await aios.rename(temp_path, final_path)
            
            # Create metadata
            file_metadata = FileMetadata(
                file_id=file_id,
                filename=file.filename,
                content_type=file.content_type or "application/octet-stream",
                size=file_size,
                checksum=checksum,
                metadata=metadata or {},
                tags=tags or [],
                created_at=time.time(),
                updated_at=time.time()
            )
            
            # Save metadata
            await self._save_metadata(file_metadata)
            
            # Publish event
            await self._publish_event("file_uploaded", {
                "file_id": file_id,
                "filename": file.filename,
                "size": file_size
            })
            
            return file_metadata
            
        except Exception as e:
            # Clean up on error
            if temp_path.exists():
                await aios.remove(temp_path)
            raise
            
    async def download_file(self, file_id: str, version: int = None) -> Tuple[Path, FileMetadata]:
        """
        Get a file for download.
        
        Args:
            file_id: ID of the file to download
            version: Optional version number (defaults to latest)
            
        Returns:
            Tuple of (file_path, metadata)
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        metadata = await self.get_file_metadata(file_id, version)
        file_path = self._get_file_path(file_id, metadata.version if version is not None else None)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_id} not found")
            
        return file_path, metadata
        
    async def get_file_metadata(self, file_id: str, version: int = None) -> FileMetadata:
        """
        Get metadata for a file.
        
        Args:
            file_id: ID of the file
            version: Optional version number (defaults to latest)
            
        Returns:
            FileMetadata object
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        metadata_path = self._get_metadata_path(file_id, version)
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata for file {file_id} not found")
            
        async with aiofiles.open(metadata_path, "r") as f:
            data = json.loads(await f.read())
            
        return FileMetadata(**data)
        
    async def list_files(
        self,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FileMetadata]:
        """
        List files with optional filtering and pagination.
        
        Args:
            tags: Optional list of tags to filter by
            skip: Number of files to skip
            limit: Maximum number of files to return
            
        Returns:
            List of FileMetadata objects
        """
        result = []
        
        # In a real implementation, this would use a database query
        # For filesystem-based storage, we'll list all metadata files
        async for file_path in self._iter_metadata_files():
            try:
                metadata = await self.get_file_metadata(file_path.stem)
                if not metadata.is_deleted:
                    if not tags or any(tag in metadata.tags for tag in tags):
                        result.append(metadata)
            except Exception as e:
                logger.error(f"Error reading metadata {file_path}: {e}")
                
        # Apply pagination
        return result[skip:skip + limit]
        
    async def delete_file(self, file_id: str, permanent: bool = False) -> bool:
        """
        Delete a file or mark it as deleted.
        
        Args:
            file_id: ID of the file to delete
            permanent: If True, permanently delete the file
            
        Returns:
            bool: True if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            metadata = await self.get_file_metadata(file_id)
            
            if permanent:
                # Remove file and metadata
                file_path = self._get_file_path(file_id)
                if file_path.exists():
                    await aios.remove(file_path)
                    
                # Remove all versions
                versions_dir = self.storage_root / "versions" / file_id
                if versions_dir.exists():
                    await aios.rmtree(versions_dir)
                    
                # Remove metadata
                metadata_path = self._get_metadata_path(file_id)
                if metadata_path.exists():
                    await aios.remove(metadata_path)
                    
                await self._publish_event("file_deleted_permanently", {
                    "file_id": file_id,
                    "filename": metadata.filename
                })
            else:
                # Mark as deleted
                metadata.is_deleted = True
                metadata.updated_at = time.time()
                await self._save_metadata(metadata)
                
                await self._publish_event("file_marked_deleted", {
                    "file_id": file_id,
                    "filename": metadata.filename
                })
                
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise
            
    async def _save_metadata(self, metadata: FileMetadata):
        """Save file metadata."""
        metadata_path = self._get_metadata_path(metadata.file_id, metadata.version)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Attempting to save metadata for file {metadata.file_id}: {metadata.dict()}")
        
        async with aiofiles.open(metadata_path, "w") as f:
            # Use model_dump_json for Pydantic v2 compatibility
            await f.write(metadata.model_dump_json(indent=2))
            
    def _get_metadata_path(self, file_id: str, version: int = None) -> Path:
        """Get the path to a file's metadata."""
        if version:
            return self.storage_root / "versions" / file_id / f"v{version}.meta"
        return self.storage_root / f"{file_id}.meta"
        
    async def _iter_metadata_files(self) -> AsyncGenerator[Path, None]:
        """Iterate over all metadata files."""
        for entry in os.scandir(self.storage_root):
            if entry.is_file() and entry.name.endswith('.meta'):
                yield Path(entry.path)
                
    async def _find_file_by_checksum(self, checksum: str) -> Optional[FileMetadata]:
        """Find a file by its checksum."""
        async for meta_path in self._iter_metadata_files():
            try:
                metadata = await self.get_file_metadata(meta_path.stem)
                if metadata.checksum == checksum and not metadata.is_deleted:
                    return metadata
            except Exception as e:
                continue
        return None
        
    async def get_file_versions(self, file_id: str) -> List[FileMetadata]:
        """Get all versions of a file."""
        versions = []
        versions_dir = self.storage_root / "versions" / file_id
        
        if not versions_dir.exists():
            return []
            
        for entry in os.scandir(versions_dir):
            if entry.is_file() and entry.name.endswith('.meta'):
                try:
                    version = int(entry.name[1:-5])  # Extract version from v1.meta
                    metadata = await self.get_file_metadata(file_id, version)
                    versions.append(metadata)
                except (ValueError, json.JSONDecodeError) as e:
                    continue
                    
        return sorted(versions, key=lambda x: x.version)
        
    async def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours."""
        temp_dir = self.storage_root / "tmp"
        cutoff = time.time() - (older_than_hours * 3600)
        count = 0
        
        if not temp_dir.exists():
            return 0
            
        for entry in os.scandir(temp_dir):
            if entry.is_file() and entry.stat().st_mtime < cutoff:
                try:
                    await aios.remove(entry.path)
                    count += 1
                except Exception as e:
                    logger.error(f"Error removing temp file {entry.path}: {e}")
                    
        return count

    async def update_metadata(self, file_id: str, metadata_update: Dict[str, Any]) -> FileMetadata:
        """
        Update the metadata for a file.
        
        Args:
            file_id: ID of the file
            metadata_update: Dictionary of metadata fields to update
            
        Returns:
            Updated FileMetadata object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If metadata_update is not a dictionary
        """
        if not isinstance(metadata_update, dict):
            raise ValueError("Metadata update must be a dictionary.")

        # Get current metadata
        metadata = await self.get_file_metadata(file_id)

        # Update metadata fields
        metadata.metadata.update(metadata_update)
        metadata.updated_at = time.time()  # Update timestamp

        # Save updated metadata
        await self._save_metadata(metadata)
        
        # Publish event
        await self._publish_event("metadata_updated", {
            "file_id": file_id,
            "metadata_update": metadata_update
        })

        return metadata

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get file system statistics.
        
        Returns:
            Dictionary containing file system stats
        """
        total_size = 0
        file_count = 0
        type_counts = {}
        version_count = 0
        
        # Count files and calculate total size
        async for file_path in self._iter_metadata_files():
            try:
                metadata = await self.get_file_metadata(file_path.stem)
                if not metadata.is_deleted:
                    file_count += 1
                    total_size += metadata.size
                    
                    # Count by file type
                    ext = metadata.filename.rsplit('.', 1)[1].lower() if '.' in metadata.filename else 'unknown'
                    type_counts[ext] = type_counts.get(ext, 0) + 1
                    
                    # Count versions
                    versions = await self.get_file_versions(metadata.file_id)
                    version_count += len(versions)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue
                
        return {
            "total_files": file_count,
            "total_size": total_size,
            "file_types": type_counts,
            "total_versions": version_count,
            "storage_path": str(self.storage_root)
        }

    async def upload_directory(
        self,
        files: List[UploadFile],
        base_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False
    ) -> List[FileMetadata]:
        """
        Upload a directory of files while maintaining the directory structure.
        
        Args:
            files: List of FastAPI UploadFile objects
            base_path: Optional base path where to store the files
            metadata: Optional file metadata to apply to all files
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of FileMetadata for all uploaded files
            
        Raises:
            ValueError: For invalid files or metadata
            IOError: For file system errors
        """
        uploaded_files = []
        
        for file in files:
            # Skip directories (they'll be created automatically)
            if not file.filename:
                continue
                
            # Construct the full path
            file_path = Path(file.filename)
            if base_path:
                file_path = Path(base_path) / file_path
                
            # Create parent directories if they don't exist
            parent_dir = self.storage_root / file_path.parent
            parent_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # Upload the file
                file_metadata = await self.upload_file(
                    file=file,
                    metadata=metadata,
                    overwrite=overwrite
                )
                uploaded_files.append(file_metadata)
                
            except Exception as e:
                logger.error(f"Error uploading file {file.filename}: {str(e)}")
                # Continue with other files even if one fails
                continue
                
        return uploaded_files

# Singleton instance
file_manager = FileManager()

async def get_file_manager() -> FileManager:
    """Dependency for FastAPI to get the file manager instance."""
    return file_manager