import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.marketplace_blog.services.s3_service import S3Service

logger = logging.getLogger(__name__)

router = APIRouter()
s3_service = S3Service()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def allowed_file(filename):
    """Проверяет, является ли расширение файла допустимым."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Загружает изображение на S3 и возвращает URL изображения. :param file: Файл изображения :return: Словарь с ключом 'image_url', содержащим URL загруженного изображения"""
    if not file:
        logger.error("No file uploaded")
        raise HTTPException(status_code=400, detail="No file uploaded")
    if not allowed_file(file.filename):
        logger.error(f"Unacceptable file extension: {file.filename}.")
        raise HTTPException(
            status_code=415,
            detail=f"Unacceptable type of file: {file.filename}. Only files with extensions are allowed: {', '.join(ALLOWED_EXTENSIONS)}.",
        )

    try:
        file_name = file.filename
        image_url = s3_service.upload_image(file.file, file_name, endpoint_url=None)
        logger.info(f"Successful download of the file: {file_name}, URL: {image_url}")
        return {"image_url": image_url}
    except Exception as e:
        logger.exception(f"There was an error when downloading the file: {str(e)}")
        raise HTTPException(
            status_code=500, detail="There was an internal server error."
        )


@router.get("/images/{file_name}")
async def get_image(file_name: str):
    """Получает URL изображения из S3. :param file_name: Имя файла изображения :return: Словарь с ключом 'image_url', содержащим URL изображения"""
    try:
        image_url = s3_service.get_image_url(file_name, endpoint_url=None)
        logger.info(
            f"Successful acquisition of image URL: {file_name}, URL: {image_url}"
        )
        return {"image_url": image_url}
    except Exception as e:
        logger.exception(f"There was an error when you get an image URL: {str(e)}")
        raise HTTPException(status_code=404, detail="Image not found.")
