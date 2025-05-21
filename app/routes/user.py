from fastapi import APIRouter, HTTPException
from typing import List
from app.models.user import User
from app.schemas.user import UserUpdate, UserInDB
from mongoengine.errors import  ValidationError, DoesNotExist
from fastapi import Depends
from app.dependencies import get_current_user

router = APIRouter()

# Get user by id
@router.get('/{user_id}', response_model=UserInDB)
def get_user(user_id: str):
    try:
        u = User.objects.get(id=user_id)
        return UserInDB(
            id=str(u.id),
            name=u.name,
            last_name=u.last_name,
            email=u.email,
            is_active=u.is_active,
            role=u.role,
            created_at=u.created_at,
            updated_at=u.updated_at
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

# Update user
@router.put('/{user_id}', response_model=UserInDB)
def update_user(user_id: str, user: UserUpdate):
    try:
        user = User.objects.get(id=user_id)
        update_data = user.dict(exclude_unset=True)
              
        user.update(**update_data)
        user.reload()
        
        return UserInDB(
            id=str(user.id),
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            is_active=user.is_active,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
# Get all users
@router.get('/', response_model=List[UserInDB])
def get_users(current_user: User = Depends(get_current_user)):
    users = User.objects.all()
    return [UserInDB(
        id=str(user.id),
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at
    ) for user in users]