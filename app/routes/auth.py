from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserLogin, UserUpdate
from app.utils.password import verify_password, get_password_hash
from app.utils.jwt import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from app.dependencies import get_current_user

router = APIRouter()

# Register user
@router.post("/register", response_model=UserInDB)
async def register(user: UserCreate):
    try:
        user_data = user.dict()
        password = user_data.pop('password')
        user_data['password_hash'] = get_password_hash(password)
        
        user = User(**user_data)
        user.save()
        
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
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

# Login user
@router.post("/login")
async def login(user: UserLogin):
    try:
        user_in_db = User.objects.get(email=user.email)
        if not verify_password(user.password, user_in_db.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user_in_db.id),
                "email": user_in_db.email,
                "role": user_in_db.role 
            },
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Update user profile
@router.put("/update-me", response_model=UserInDB)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        update_data = user_update.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['password_hash'] = get_password_hash(update_data.pop('password'))
        
        current_user.update(**update_data)
        current_user.reload()
        
        return UserInDB(
            id=str(current_user.id),
            name=current_user.name,
            last_name=current_user.last_name,
            email=current_user.email,
            is_active=current_user.is_active,
            role=current_user.role,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Email already exists")

# Delete user
""" @router.delete("/user/{user_id}")
async def delete_user(user_id: str):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return {"message": "User deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found") """
