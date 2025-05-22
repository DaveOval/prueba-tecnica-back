from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Body
from fastapi.responses import FileResponse
from app.models.images import Image
from app.models.user import User
from app.dependencies import get_current_user
from app.services.storage import save_upload_file
from app.services.image_processor import proccess_image
from typing import List
from app.utils.validate_image import validate_image
from app.utils.logger import setup_logger
import os
import base64
from pydantic import BaseModel


class FilterRequest(BaseModel):
    filter_name: str


router = APIRouter()
logger = setup_logger("images")

def normalize_path(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")

# Upload image
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Image upload attempt by user: {current_user.email}")
    validate_image(file)
    
    # Create directories if they don't exist
    upload_dir = normalize_path(os.path.join("uploads", "original"))
    processed_dir = normalize_path(os.path.join("uploads", "processed"))
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    # Save original file
    original_path = save_upload_file(file, upload_dir)
    original_path = normalize_path(original_path)
    
    # Create processed path
    file_ext = file.filename.split('.')[-1]
    processed_filename = f"processed_{os.path.basename(original_path)}"
    processed_path = normalize_path(os.path.join(processed_dir, processed_filename))
    
    # Create image record
    image = Image(
        user_id=str(current_user.id),
        original_filename=file.filename,
        original_path=original_path,
        processed_path=processed_path,
        filter_name=None,
        filter_value=None
    )
    image.save()
    
    logger.info(f"Image uploaded successfully: {file.filename} by the user: {current_user.email}")
    return {
        "message": "Image uploaded successfully",
        "image_id": str(image.id)
    }

# Process image
@router.post("/{image_id}/process")
async def process_image(
    image_id: str,
    filter_request: FilterRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Image processing attempt {image_id} with filter {filter_request.filter_name}")
        image = Image.objects.get(id=image_id)
        
        # Verify ownership
        if str(image.user_id) != str(current_user.id):
            logger.warning(f"Attempt at unauthorized image processing {image_id} by user {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to process this image"
            )
        
        # Normalize paths
        original_path = normalize_path(image.original_path)
        processed_path = normalize_path(image.processed_path)
        
        # Verify original image exists
        if not os.path.exists(original_path):
            logger.error(f"Original image not found in the path: {original_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Original image file not found at path: {original_path}"
            )
        
        # Process image
        try:
            proccess_image(original_path, processed_path, filter_request.filter_name)
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing image: {str(e)}"
            )
        
        # Verify processed image was created
        if not os.path.exists(processed_path):
            logger.error(f"Error saving processed image to path: {processed_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving processed image at path: {processed_path}"
            )
        
        # Update image record
        image.filter_name = filter_request.filter_name
        image.save()
        
        logger.info(f"Image {image_id} successfully processed with {filter_request.filter_name} filter")
        return {
            "message": "Image processed successfully",
            "filter": filter_request.filter_name
        }
        
    except Image.DoesNotExist:
        logger.warning(f"Attempt to process non-existent image: {image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

# Get user images
@router.get("/", response_model=List[dict])
async def get_user_images(current_user: User = Depends(get_current_user)):
    logger.info(f"Getting list of images for the user: {current_user.email}")
    images = Image.objects(user_id=str(current_user.id))
    return [
        {
            "id": str(img.id),
            "original_filename": img.original_filename,
            "original_path": img.original_path,
            "processed_path": img.processed_path,
            "filter_name": img.get_filter_name(),
            "filter_value": img.get_filter_value(),
            "uploaded_at": img.uploaded_at
        }
        for img in images
    ]

# Delete image
@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Image deletion attempt {image_id} by user: {current_user.email}")
        image = Image.objects.get(id=image_id)
        
        # Verify ownership
        if str(image.user_id) != str(current_user.id):
            logger.warning(f"Unauthorized image removal attempt {image_id} by user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this image"
            )
        
        # Delete files
        if os.path.exists(image.original_path):
            os.remove(image.original_path)
        if os.path.exists(image.processed_path):
            os.remove(image.processed_path)
        
        # Delete record
        image.delete()
        
        logger.info(f"Image {image_id} successfully removed")
        return {"message": "Image deleted successfully"}
        
    except Image.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent image: {image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

@router.get("/{image_id}/serve")
async def serve_image(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Image request {image_id} by user: {current_user.email}")
        image = Image.objects.get(id=image_id)
        
        # Verify ownership
        if str(image.user_id) != str(current_user.id):
            logger.warning(f"Attempt to access an unauthorized image {image_id} by user {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this image"
            )
        
        # Normalize paths
        processed_path = normalize_path(image.processed_path)
        original_path = normalize_path(image.original_path)
        
        # Check if processed file exists, if not use original
        file_path = processed_path if os.path.exists(processed_path) else original_path
        
        # Verify the file exists
        if not os.path.exists(file_path):
            logger.error(f"Image file not found in the path: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found at path: {file_path}"
            )
        
        # Read the image file and convert to base64
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading image file: {str(e)}"
            )
        
        # Get the file extension to determine the MIME type
        file_ext = image.original_filename.split('.')[-1].lower()
        mime_type = f"image/{file_ext}"
        
        # Return the base64 image with its MIME type
        return {
            "image_data": f"data:{mime_type};base64,{encoded_string}",
            "filename": image.original_filename
        }
        
    except Image.DoesNotExist:
        logger.warning(f"Attempt to access non-existent image: {image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found in database"
        )

# Get image file in binary format (base64)
@router.get("/{image_id}/file")
async def get_image_file(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Image file request {image_id} by user: {current_user.email}")
        image = Image.objects.get(id=image_id)
        
        # Verify ownership
        if str(image.user_id) != str(current_user.id):
            logger.warning(f"Unauthorized image file access attempt {image_id} by user {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this image"
            )
        
        # Check if processed file exists, if not use original
        file_path = image.processed_path if os.path.exists(image.processed_path) else image.original_path
        file_path = file_path.replace("\\", "/")
        
        if not os.path.exists(file_path):
            logger.error(f"Image file not found in path: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found at path: {file_path}"
            )
        
        logger.info(f"Image file {image_id} successfully sent")
        return FileResponse(
            file_path,
            media_type=f"image/{image.original_filename.split('.')[-1].lower()}",
            filename=image.original_filename
        )
        
    except Image.DoesNotExist:
        logger.warning(f"Attempt to access non-existent image file: {image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found in database"
        )