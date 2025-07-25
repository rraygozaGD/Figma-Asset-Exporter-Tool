import logging
import os
from datetime import datetime
def load_env():
    from dotenv import load_dotenv
    import os
    load_dotenv()

def is_image_url(url):
    image_extensions = ('.svg', '.ico', '.jpg', '.png', '.gif')
    return url.lower().endswith(image_extensions)

def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), '..','..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    timestamp =datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"figma_download_{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return log_path
