"""Context Management Routes for FastMCP Server.

This module provides the API endpoints for managing context data in the FastMCP server.
It includes operations for setting, getting, and deleting context items, both individually
and in bulk, with support for filtering and pagination.
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends, status
from fastapi.responses import JSONResponse
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from pydantic import field_serializer

from app.core.context_manager import mcp_context_manager
from app.models.pydantic_models import ContextItem, ContextBulkOperation, ContextQuery, SearchResults, SearchResultItem
from app.core.file_manager import file_manager

# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["context"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    }
)

# Configure logging
logger = logging.getLogger(__name__)

class ContextFilter(BaseModel):
    prefix: Optional[str] = None
    namespace: Optional[str] = None

class ContextResponse(BaseModel):
    """Response model for context operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime) -> str:
        return dt.isoformat()

class BulkContextItems(BaseModel):
    items: List[ContextItem]

    @field_serializer('items')
    def serialize_items(self, items: List[ContextItem]) -> List[Dict[str, Any]]:
        return [item.model_dump() for item in items]

@router.post(
    "/context",
    response_model=ContextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set or update a context item",
    response_description="The context item was successfully set or updated"
)
async def set_context_item(item: ContextItem) -> ContextResponse:
    """
    Set or update a specific context item.

    - **key**: Unique identifier for the context item
    - **value**: The value to store (any JSON-serializable data)
    - **namespace**: Optional namespace for organizing context items
    - **ttl**: Optional time-to-live in seconds
    - **metadata**: Optional additional metadata
    """
    try:
        await mcp_context_manager.async_set_context(
            key=item.key,
            value=item.value,
            namespace=item.namespace,
            ttl=item.ttl,
            metadata=item.metadata
        )
        return ContextResponse(
            success=True,
            message=f"Context item '{item.key}' set successfully",
            data={"key": item.key}
        )
    except ValueError as e:
        logger.error(f"Error setting context item {item.key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error setting context item {item.key}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post(
    "/context/bulk",
    response_model=ContextResponse,
    status_code=status.HTTP_207_MULTI_STATUS,
    summary="Bulk set or update context items"
)
async def bulk_set_context_items(items: BulkContextItems) -> ContextResponse:
    """
    Set or update multiple context items in a single operation.

    - **items**: List of context items to set/update
    - Returns: Results for each operation
    """
    results = []
    for item in items.items:
        try:
            await mcp_context_manager.async_set_context(
                key=item.key,
                value=item.value,
                namespace=item.namespace,
                ttl=item.ttl,
                metadata=item.metadata
            )
            results.append({
                "key": item.key,
                "status": "success",
                "message": f"Context item '{item.key}' set successfully"
            })
        except Exception as e:
            logger.error(f"Error setting context item {item.key}: {str(e)}")
            results.append({
                "key": item.key,
                "status": "error",
                "message": str(e)
            })
    
    return ContextResponse(
        success=all(r["status"] == "success" for r in results),
        message="Bulk operation completed",
        data={"results": results}
    )

@router.get(
    "/context/{key}",
    response_model=ContextResponse,
    summary="Get a context item by key"
)
async def get_context_item(
    key: str,
    namespace: Optional[str] = None,
    include_metadata: bool = False
) -> ContextResponse:
    """
    Retrieve a specific context item by its key.

    - **key**: The key of the context item to retrieve
    - **namespace**: Optional namespace filter
    - **include_metadata**: Whether to include metadata in the response
    """
    try:
        value = await mcp_context_manager.async_get_context(
            key=key,
            namespace=namespace
        )
        
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context item '{key}' not found"
            )
            
        response_data = {"key": key, "value": value}
        
        if include_metadata:
            metadata = await mcp_context_manager.get_metadata(key)
            if metadata:
                response_data["metadata"] = metadata
        
        return ContextResponse(
            success=True,
            message="Context item retrieved successfully",
            data=response_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving context item {key}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the context item"
        )

@router.get(
    "/context",
    response_model=ContextResponse,
    summary="List context items with filtering"
)
async def list_context_items(
    prefix: Optional[str] = Query(
        None,
        description="Filter keys by prefix"
    ),
    namespace: Optional[str] = Query(
        None,
        description="Filter by namespace"
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
) -> ContextResponse:
    """
    List context items with optional filtering and pagination.

    - **prefix**: Filter keys by prefix
    - **namespace**: Filter by namespace
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return (max 1000)
    """
    try:
        # Create filter object
        context_filter = ContextFilter(
            prefix=prefix,
            namespace=namespace
        )
        
        # Get items with pagination
        items = await mcp_context_manager.async_list_context(
            context_filter=context_filter,
            skip=skip,
            limit=limit
        )
        
        # Get total count for pagination
        total = await mcp_context_manager.async_count_context(
            context_filter=context_filter
        )
        
        return ContextResponse(
            success=True,
            message=f"Found {len(items)} context items",
            data={
                "items": items,
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(items)) < total
                }
            }
        )
    except Exception as e:
        logger.exception("Error listing context items")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while listing context items"
        )

@router.delete(
    "/context/{key}",
    response_model=ContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a context item by key"
)
async def delete_context_item(
    key: str,
    namespace: Optional[str] = None
) -> ContextResponse:
    """
    Delete a specific context item by its key.

    - **key**: The key of the context item to delete
    - **namespace**: Optional namespace filter
    """
    try:
        # Check if item exists
        existing = await mcp_context_manager.async_get_context(key, namespace)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context item '{key}' not found"
            )
            
        # Delete the item
        await mcp_context_manager.async_delete_context(key, namespace)
        
        return ContextResponse(
            success=True,
            message=f"Context item '{key}' deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting context item {key}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the context item"
        )

@router.delete(
    "/context",
    response_model=ContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk delete context items"
)
async def bulk_delete_context_items(
    keys: List[str] = Body(..., embed=True),
    namespace: Optional[str] = None
) -> ContextResponse:
    """
    Delete multiple context items by their keys.

    - **keys**: List of keys to delete
    - **namespace**: Optional namespace filter
    """
    results = []
    for key in keys:
        try:
            # Check if item exists
            existing = await mcp_context_manager.async_get_context(key, namespace)
            if existing is None:
                results.append({
                    "key": key,
                    "status": "not_found",
                    "message": f"Context item '{key}' not found"
                })
                continue
                
            # Delete the item
            await mcp_context_manager.async_delete_context(key, namespace)
            results.append({
                "key": key,
                "status": "success",
                "message": f"Context item '{key}' deleted successfully"
            })
        except Exception as e:
            logger.error(f"Error deleting context item {key}: {str(e)}")
            results.append({
                "key": key,
                "status": "error",
                "message": str(e)
            })
    
    return ContextResponse(
        success=all(r["status"] in ("success", "not_found") for r in results),
        message="Bulk delete operation completed",
        data={"results": results}
    )

@router.get("/search", response_model=SearchResults)
async def search_context(
    query: str,
    file_types: Optional[List[str]] = Query(None, description="Filter by file types"),
    date_from: Optional[datetime] = Query(None, description="Filter by start date"),
    date_to: Optional[datetime] = Query(None, description="Filter by end date"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, date, size"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Search across files and context with advanced filtering and sorting.
    
    - **query**: Search term
    - **file_types**: Filter by file types (e.g., pdf, doc, txt)
    - **date_from**: Filter by start date
    - **date_to**: Filter by end date
    - **tags**: Filter by tags
    - **sort_by**: Sort by relevance, date, or size
    - **sort_order**: Sort order (asc or desc)
    - **skip**: Number of results to skip
    - **limit**: Maximum number of results to return
    """
    try:
        # Build search query
        search_query = SearchQuery(
            query=query,
            file_types=file_types,
            date_from=date_from,
            date_to=date_to,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        # Perform search
        results = await mcp_context_manager.search(search_query)
        
        # Add metadata to results
        for result in results.items:
            if result.type == "file":
                try:
                    file_metadata = await file_manager.get_file_metadata(result.id)
                    result.metadata = file_metadata.dict()
                except FileNotFoundError:
                    continue
                    
        return SearchResults(
            query=query,
            total=len(results.items),
            items=results.items
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )