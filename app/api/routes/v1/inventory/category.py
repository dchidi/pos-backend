from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.inventory.category import Category  # your Beanie model
from app.schemas.inventory.category import(
    CategoryResponse, CategoryCreate, CategoryUpdate,
    CategoryListResponse
)


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category_in: CategoryCreate):
    """Create a new category."""
    category = Category(**category_in.model_dump())
    await category.insert()
    return category


@router.get(
    "/",
    response_model=CategoryListResponse,
)
async def list_categories(skip: int = 0, limit: int = 100):
    """List non-deleted categories with pagination, returning total count."""
    # Count total non-deleted categories
    total = await Category.find(Category.is_deleted == False).count()
    # Retrieve paginated items
    items = (
        await Category.find(Category.is_deleted == False)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return CategoryListResponse(total=total, items=items)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
async def get_category(category_id: str):
    """Retrieve a category by its ID."""
    category = await Category.get(category_id)
    if not category or category.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
async def update_category(
    category_id: str,
    category_in: CategoryUpdate,
):
    """Update an existing category."""
    category = await Category.get(category_id)
    if not category or category.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    await category.save()
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(category_id: str):
    """Soft-delete a category."""
    category = await Category.get(category_id)
    if not category or category.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    category.is_deleted = True
    await category.save()
    return None

