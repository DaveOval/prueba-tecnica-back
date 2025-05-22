from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserLogin, UserUpdate
from app.utils.password import verify_password, get_password_hash
from app.utils.jwt import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from app.dependencies import get_current_user
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("auth")

# Register user
@router.post("/register", response_model=UserInDB)
async def register(user: UserCreate):
    try:
        logger.info(f"Attempted registration for email: {user.email}")
        user_data = user.dict()
        password = user_data.pop('password')
        user_data['password_hash'] = get_password_hash(password)
        
        user = User(**user_data)
        user.save()
        
        logger.info(f"User register succesfully: {user.email}")
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
        logger.warning(f"Registration attempt with duplicate email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already exists")
    except ValidationError as e:
        logger.error(f"Validation error in register: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

# Login user
@router.post("/login")
async def login(response: Response, user: UserLogin):
    try:
        logger.info(f"Attempting login for email: {user.email}")
        user_in_db = User.objects.get(email=user.email)
        
        # Check if the user is active
        if not user_in_db.is_active:
            logger.warning(f"Login attempt for inactive user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        password_valid = verify_password(user.password, user_in_db.password_hash)
        if not password_valid:
            logger.warning(f"Invalid password for user: {user.email}")
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
        
        # Set cookie with the JWT token
        response.set_cookie(
            key="auth-token",
            value=access_token,
            httponly=True,
            secure=False, 
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60 
        )
        
        logger.info(f"Successful login for user: {user.email}")
        return {
            "message": "Login successful",
            "user": {
                "id": str(user_in_db.id),
                "email": user_in_db.email,
                "name": user_in_db.name,
                "last_name": user_in_db.last_name,
                "role": user_in_db.role,
                "token": access_token
            }
        }
        
    except DoesNotExist:
        logger.warning(f"Login attempt for non-existent user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Update user profile
@router.put("/update-me", response_model=UserInDB)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Attempt to update profile for user: {current_user.email}")
        update_data = user_update.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['password_hash'] = get_password_hash(update_data.pop('password'))
        
        current_user.update(**update_data)
        current_user.reload()
        
        logger.info(f"Profile successfully updated for user: {current_user.email}")
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
        logger.error(f"Validation error in profile update: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except NotUniqueError:
        logger.warning(f"Update attempt with duplicate email: {current_user.email}")
        raise HTTPException(status_code=400, detail="Email already exists")

# Delete user
# Well i dont think this is a good idea, but here its for the fure
# And i dont really have time to implement in the next app or here in the API 
# So i hope someone read this :D
""" @router.delete("/user/{user_id}")
async def delete_user(user_id: str):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return {"message": "User deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found") """
