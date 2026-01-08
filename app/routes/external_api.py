from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.item_model import Item
from app.schemas.item_schema import ItemResponse, ExternalApiResponse
import requests
import os
from typing import List

router = APIRouter()

@router.get("/external/fetch-data/{item_id}", response_model=ItemResponse)
def fetch_external_data(item_id: int, db: Session = Depends(get_db)):
    """
    Fetch data from external API and update the item with external data
    This endpoint demonstrates integration with an external API (using JSONPlaceholder as example)
    """
    # Get the existing item
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        # Fetch data from external API (using JSONPlaceholder as example)
        # In a real application, this would be an LLM provider, GitHub API, or other service
        external_url = f"https://jsonplaceholder.typicode.com/posts/{item_id}"
        response = requests.get(external_url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch data from external API"
            )
        
        external_data = response.json()
        
        # Update the item with external data
        db_item.external_data = str(external_data)
        db.commit()
        db.refresh(db_item)
        
        return db_item
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error connecting to external API: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing external data: {str(e)}"
        )


@router.get("/external/posts", response_model=List[ExternalApiResponse])
def get_external_posts():
    """
    Get posts from external API without storing in local database
    """
    try:
        # Fetch posts from external API
        external_url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(external_url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch posts from external API"
            )
        
        posts = response.json()
        
        # Return only the first 5 posts to avoid too much data
        return [ExternalApiResponse(**post) for post in posts[:5]]
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error connecting to external API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing external data: {str(e)}"
        )