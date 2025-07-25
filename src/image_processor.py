import os
import requests
import logging
from urllib.parse import urlparse
class ImageProcessor:
    def __init__(self, download_path):
        self.download_path = download_path
        self.logger = logging.getLogger(__name__)

        if not os.path.exists(download_path):
            os.makedirs(download_path)
            self.logger.info(f"Download directory created at: {download_path}")
        else:
            self.logger.info(f"Download directory already exists: {download_path}")
            
    def download_image(self, image_data):
        if isinstance(image_data, dict):
            image_url = image_data.get('url')
            image_name = image_data.get('name', 'unknown')
            node_id = image_data.get('id', 'unknown')
            self.logger.info(f"Attempting to download exported node '{image_name}' with ID {node_id} from URL: {image_url}")
        else:
            image_url = image_data
            image_name = None
            self.logger.info(f"Attempting to download image from URL: {image_url}")
        
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                self.logger.info(f"Successfully downloaded image from {image_url}")
                self.save_image(image_url, response.content, image_name)
            else:
                self.logger.error(f"Failed to download image from {image_url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading image from {image_url}: {str(e)}")

    def save_image(self, image_url, content, custom_name=None):
        try:
            if custom_name:
                safe_name = "".join(c for c in custom_name if c.isalnum() or c in (' ','-','_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                image_name = f"{safe_name}.png"
            else:
                parsed_url = urlparse(image_url)
                image_name = os.path.basename(parsed_url.path)

                if not image_name or '.' not in image_name:
                    image_name = f"image_{hash(image_url) % 100000}.png"
            
            file_path = os.path.join(self.download_path, image_name)

            counter = 1
            original_name = image_name
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_name)
                image_name = f"{name}_{counter}{ext}"
                file_path = os.path.join(self.download_path, image_name)
                counter += 1
            with open(file_path, 'wb') as image_file:
                image_file.write(content)
            self.logger.info(f"Image saved as {image_name} at {self.download_path}")
        except Exception as e:
            self.logger.error(f"Error saving image {image_name}: {str(e)}")
            
