import os
from figma_client import FigmaClient
from image_processor import ImageProcessor
from utils.helpers import load_env, setup_logging
import logging

def main():
    log_file_path = setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("====Starting Figma Image Download Process====")

        load_env()

        figma_token = os.getenv('FIGMA_API_TOKEN')
        figma_file_key = os.getenv('FIGMA_FILE_KEY')
        
        download_path = os.getenv('DOWNLOAD_PATH', 'downloads')
        if not figma_token:
            logger.error("Figma PAT enviroment variable not set")
            return
        if not figma_file_key:
            logger.error("Figma ID file environment variable not set")
            return
        logger.info(f"Configuration: File Key={figma_file_key}, Download Path ={download_path}")

        figma_client = FigmaClient(figma_token)
        logger.info("Figma cliente initialized")
        image_urls = figma_client.get_images(figma_file_key)
        image_processor = ImageProcessor(download_path)

        successful_downloads = 0
        failed_downloads = 0

        for i, url in enumerate(image_urls, 1):
            logger.info(f"Processing image {i}/{len(image_urls)}")
            try:
                image_processor.download_image(url)
                successful_downloads+=1
            except Exception as e:
                logger.error(f"Failed to download image {i}: {str(e)}")
                failed_downloads+=1
        
        logger.info(f"=======Download Process completed===")
        logger.info(f"Total images found: {len(image_urls)}")
        logger.info(f"Successfully downloaded: {successful_downloads}")
        logger.info(f"Failed downloads: {failed_downloads}")
    except Exception as e:
        logger.error(f"Application failed with error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()