from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from app.utils.password import verify_password, get_password_hash
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Register user
@router.post("/register", response_model=UserInDB)
async def register(user: UserCreate):
    try:
        user_data = user.dict()
        password = user_data.pop('password')
        user_data['password_hash'] = get_password_hash(password)
        
        u = User(**user_data)
        u.save()
        
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
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

# Login user
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = User.objects.get(email=form_data.username)
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"message": "Login successful"}
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Delete user
@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return {"message": "User deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
