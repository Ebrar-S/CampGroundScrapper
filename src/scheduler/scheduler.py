from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import logging
from src.services.campground_service import validate_data, save_update_to_db
from src.scraper.scraper import fetch_all_pages

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def scheduled_scraper():
    logger.info("--------- Scheduled Scraper Started ---------")
    
    try:
        data = asyncio.run(fetch_all_pages())
        
        logger.info(f"Fetched {len(data)} records.")
        
        for item in data:
            campground = validate_data(item)
            if campground:
                save_update_to_db(campground)
            else:
                logger.warning(f"Invalid data for campground: {item}")

    except Exception as e:
        logger.error(f"Error during scheduled scraper execution: {e}")

scheduler.add_job(scheduled_scraper, 'interval', hours=24)  # Run daily
scheduler.start()
