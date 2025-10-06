"""File Management Routes for FastMCP Server.

This module provides API endpoints for managing files in the FastMCP server.
It includes operations for uploading, downloading, listing, and managing files
with support for versioning, metadata, and file system monitoring.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, BinaryIO
from fastapi import (
    APIRouter, 
    HTTPException, 
    UploadFile, 
    File, 
    Form, 
    Query, 
    Depends, 
    status,
    BackgroundTasks,
    Body
)
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import aiofiles
import shutil
import json
from pydantic import field_serializer

from app.core.file_manager import file_manager
from app.core.context_manager import mcp_context_manager

# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["files"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"},
        status.HTTP_404_NOT_FOUND: {"description": "File not found"},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": "File too large"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    }
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json', 
    'py', 'js', 'html', 'css', 'md', 'yaml', 'yml',
    'xlsx', 'xls', 'xlsm', 'xlsb',  # Excel formats
    'doc', 'docx',  # Word formats
    'ppt', 'pptx',  # PowerPoint formats
    'zip', 'rar'    # Archive formats
}

class FileResponseModel(BaseModel):
    """Response model for file operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime) -> str:
        return dt.isoformat()

class FileInfo(BaseModel):
    """File information model."""
    filename: str
    size: int
    content_type: Optional[str] = None
    last_modified: datetime
    metadata: Optional[Dict[str, Any]] = None
    versions: Optional[List[Dict[str, Any]]] = None

@router.get(
    "/files",
    response_model=FileResponseModel,
    summary="List all files",
    description="Retrieve a list of all files with optional filtering and pagination."
)
async def list_files(
    prefix: Optional[str] = Query(
        None,
        description="Filter files by prefix"
    ),
    extension: Optional[str] = Query(
        None,
        description="Filter by file extension"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of items to skip for pagination"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of items to return"
    )
) -> FileResponseModel:
    """
    List all files with optional filtering and pagination.
    
    - **prefix**: Filter files by path prefix
    - **extension**: Filter by file extension
    - **skip**: Number of items to skip (pagination)
    - **limit**: Maximum number of items to return (1-1000)
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Get list of files
        files = await file_manager.list_files(
            prefix=prefix,
            extension=extension,
            skip=skip,
            limit=limit
        )

        # Get total count for pagination
        total = await file_manager.count_files(
            prefix=prefix,
            extension=extension
        )

        return FileResponseModel(
            success=True,
            message=f"Found {len(files)} files",
            data={
                "files": files,
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(files)) < total
                }
            }
        )
    except Exception as e:
        logger.exception("Error listing files")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while listing files"
        )

@router.post(
    "/files/upload",
    response_model=FileResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description="Upload a new file or update an existing one."
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    path: Optional[str] = Form(None),
    overwrite: bool = Form(False),
    metadata: Optional[str] = Form(None)
) -> FileResponseModel:
    """
    Upload a file to the server.
    
    - **file**: The file to upload
    - **path**: Optional path where to store the file
    - **overwrite**: Whether to overwrite if file exists (default: False)
    - **metadata**: Optional JSON string with file metadata
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Validate file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
            )

        # Validate file extension
        file_extension = Path(file.filename).suffix[1:].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_extension}' is not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Parse metadata
        file_metadata = {}
        if metadata:
            try:
                file_metadata = json.loads(metadata)
                # Ensure the parsed metadata is a dictionary
                if not isinstance(file_metadata, dict):
                    raise ValueError("Metadata must be a JSON object (dictionary).")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid metadata format. Must be a valid JSON object."
                )
            except ValueError as e:
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid metadata format: {e}"
                )

        # Determine file path
        file_path = Path(path) / file.filename if path else file.filename

        # Save the file
        saved_file_info = await file_manager.upload_file(
            file=file,
            metadata=file_metadata,
            overwrite=overwrite
        )

        # Update context if this is a parse request
        # Check if the file extension is one of the types we can parse
        parseable_extensions = ('.txt', '.md', '.csv', '.json')
        if saved_file_info.filename.lower().endswith(parseable_extensions):
            background_tasks.add_task(
                update_context_for_file,
                 saved_file_info.filename, # Pass the filename saved by the manager
                "upload"
            )

        return FileResponseModel(
            success=True,
            message=f"File '{file.filename}' uploaded successfully",
            data={
                "filename": str(file_path),
                "size": file_size,
                 "content_type": file.content_type,
                 "metadata": file_metadata
                 # If file_manager.save_file returns more info (like file_id, full_path, etc.), add it here:
                 # "file_id": saved_file_info.file_id,
                 # "full_path": saved_file_info.full_path,
                 # "upload_time": saved_file_info.upload_time
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the file: {str(e)}"
        )

@router.get(
    "/files/{file_path:path}",
    response_class=FileResponse,
    summary="Download a file",
    description="Download a file by its path."
)
async def download_file(
    file_path: str,
    download: bool = Query(False, description="Force download with Content-Disposition header")
) -> FileResponse:
    """
    Download a file by its path.
    
    - **file_path**: Path to the file to download
    - **download**: If true, forces download with Content-Disposition header
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        if not await file_manager.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )

        # Get file metadata
        metadata = await file_manager.get_metadata(file_path)
        content_type = metadata.get('content_type', 'application/octet-stream')

        # Update last accessed time
        await file_manager.update_access_time(file_path)

        # Return file response
        return FileResponse(
            path=await file_manager.get_file_path(file_path),
            filename=os.path.basename(file_path) if download else None,
            media_type=content_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error downloading file '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while downloading the file: {str(e)}"
        )

@router.get(
    "/files/{file_path:path}/info",
    response_model=FileResponseModel,
    summary="Get file information",
    description="Get detailed information about a file including metadata and versions."
)
async def get_file_info(file_path: str) -> FileResponseModel:
    """
    Get detailed information about a file.
    
    - **file_path**: Path to the file
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        if not await file_manager.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )

        # Get file info
        file_info = await file_manager.get_file_info(file_path)
        
        # Get file versions if versioning is enabled
        versions = None
        if file_manager.enable_versioning:
            versions = await file_manager.get_file_versions(file_path)

        return FileResponseModel(
            success=True,
            message="File information retrieved successfully",
            data={
                **file_info.dict(),
                "versions": versions
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting file info for '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting file information: {str(e)}"
        )

@router.delete(
    "/files/{file_path:path}",
    response_model=FileResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Delete a file",
    description="Delete a file by its path."
)
async def delete_file(
    file_path: str,
    permanent: bool = Query(False, description="Permanently delete the file (bypass trash)")
) -> FileResponseModel:
    """
    Delete a file by its path.
    
    - **file_path**: Path to the file to delete
    - **permanent**: If true, permanently deletes the file (bypasses trash)
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        if not await file_manager.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )

        # Delete the file
        await file_manager.delete_file(file_path, permanent=permanent)

        return FileResponseModel(
            success=True,
            message=f"File '{file_path}' {'permanently deleted' if permanent else 'moved to trash'} successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting file '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the file: {str(e)}"
        )

@router.post(
    "/files/{file_path:path}/parse",
    response_model=FileResponseModel,
    summary="Parse file content",
    description="Parse the content of a file and update the context."
)
async def parse_file(
    file_path: str,
    background_tasks: BackgroundTasks
) -> FileResponseModel:
    """
    Parse the content of a file and update the context.
    
    - **file_path**: Path to the file to parse
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        if not await file_manager.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )

        # Process file in background
        background_tasks.add_task(
            update_context_for_file,
            file_path,
            "parse"
        )

        return FileResponseModel(
            success=True,
            message=f"File '{file_path}' is being processed",
            data={
                "filename": file_path,
                "status": "processing"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error parsing file '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the file: {str(e)}"
        )

@router.patch(
    "/files/{file_path:path}/metadata",
    response_model=FileResponseModel,
    summary="Update file metadata",
    description="Update the metadata for a specific file."
)
async def update_file_metadata(
    file_path: str,
    metadata_update: Dict[str, Any] = Body(..., description="Dictionary of metadata fields to update")
) -> FileResponseModel:
    """
    Update the metadata for a specific file.
    
    - **file_path**: Path to the file
    - **metadata_update**: Dictionary of metadata fields to update
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Assuming file_path can be used to get the file_id by the manager
        # You might need a method in FileManager to get file_id from path if not direct mapping
        # For now, let's assume file_path is the file_id or can be resolved to it.
        # A more robust implementation might involve looking up the file by path first to get its ID.
        
        updated_metadata = await file_manager.update_metadata(
            file_id=file_path, # This might need adjustment based on how file_manager resolves IDs from paths
            metadata_update=metadata_update
        )

        return FileResponseModel(
            success=True,
            message="File metadata updated successfully",
            data={
                "file_path": file_path,
                "metadata": updated_metadata.metadata
            }
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_path}' not found"
        )
    except ValueError as e:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metadata update: {e}"
        )
    except Exception as e:
        logger.exception(f"Error updating metadata for '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating file metadata: {str(e)}"
        )

@router.get(
    "/files/{file_path:path}/versions",
    response_model=FileResponseModel,
    summary="List file versions",
    description="Get a list of all versions of a specific file."
)
async def list_file_versions(file_path: str) -> FileResponseModel:
    """
    Get a list of all versions of a specific file.
    
    - **file_path**: Path to the file
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Get all versions of the file
        versions = await file_manager.get_file_versions(file_path)
        
        if not versions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No versions found for file '{file_path}'"
            )

        return FileResponseModel(
            success=True,
            message=f"Found {len(versions)} versions",
            data={
                "file_path": file_path,
                "versions": [v.dict() for v in versions]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing versions for '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while listing file versions: {str(e)}"
        )

@router.get(
    "/files/{file_path:path}/versions/{version}",
    response_class=FileResponse,
    summary="Download specific version",
    description="Download a specific version of a file."
)
async def download_file_version(
    file_path: str,
    version: int,
    download: bool = Query(False, description="Force download with Content-Disposition header")
) -> FileResponse:
    """
    Download a specific version of a file.
    
    - **file_path**: Path to the file
    - **version**: Version number to download
    - **download**: If true, forces download with Content-Disposition header
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Get file and metadata for specific version
        file_path_obj, metadata = await file_manager.download_file(file_path, version)
        
        if not file_path_obj.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} of file '{file_path}' not found"
            )

        # Update last accessed time
        await file_manager.update_access_time(file_path)

        # Return file response
        return FileResponse(
            path=str(file_path_obj),
            filename=os.path.basename(file_path) if download else None,
            media_type=metadata.content_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error downloading version {version} of file '{file_path}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while downloading the file version: {str(e)}"
        )

@router.post(
    "/files/upload-directory",
    response_model=FileResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a directory",
    description="Upload multiple files while maintaining directory structure."
)
async def upload_directory(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    path: Optional[str] = Form(None),
    overwrite: bool = Form(False),
    metadata: Optional[str] = Form(None)
) -> FileResponseModel:
    """
    Upload a directory of files to the server.
    
    - **files**: List of files to upload (maintains directory structure)
    - **path**: Optional base path where to store the files
    - **overwrite**: Whether to overwrite if files exist (default: False)
    - **metadata**: Optional JSON string with file metadata
    """
    try:
        if file_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )

        # Validate total size of all files
        total_size = 0
        for file in files:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            total_size += file_size
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File '{file.filename}' exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
                )

        # Parse metadata
        file_metadata = {}
        if metadata:
            try:
                file_metadata = json.loads(metadata)
                if not isinstance(file_metadata, dict):
                    raise ValueError("Metadata must be a JSON object (dictionary).")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid metadata format. Must be a valid JSON object."
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid metadata format: {e}"
                )

        # Upload the directory
        uploaded_files = await file_manager.upload_directory(
            files=files,
            base_path=path,
            metadata=file_metadata,
            overwrite=overwrite
        )

        # Update context for parseable files
        parseable_extensions = ('.txt', '.md', '.csv', '.json')
        for file_info in uploaded_files:
            if file_info.filename.lower().endswith(parseable_extensions):
                background_tasks.add_task(
                    update_context_for_file,
                    file_info.filename,
                    "upload"
                )

        return FileResponseModel(
            success=True,
            message=f"Successfully uploaded {len(uploaded_files)} files",
            data={
                "uploaded_files": [
                    {
                        "filename": f.filename,
                        "size": f.size,
                        "content_type": f.content_type,
                        "metadata": f.metadata
                    } for f in uploaded_files
                ],
                "total_size": total_size,
                "base_path": path
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading directory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the directory: {str(e)}"
        )

async def update_context_for_file(file_path: str, action: str) -> None:
    """Helper function to update context for a file."""
    try:
        # Read file content
        content = await file_manager.read_file(file_path)
        if not content:
            logger.warning(f"File '{file_path}' is empty")
            return

        # Update context with file content
        context_key = f"file:{file_path}:{action}"
        await mcp_context_manager.async_set_context(
            key=context_key,
            value={
                "content": content,
                "path": file_path,
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Updated context for file '{file_path}' with action '{action}'")

    except Exception as e:
        logger.exception(f"Error updating context for file '{file_path}': {str(e)}")
        # Don't raise exception as this is running in background

# --- FILE METADATA FEATURE (Not implemented, placeholder for future expansion) ---
# To expand file metadata, add more fields to the metadata dict and expose endpoints for metadata search and update.