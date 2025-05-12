import httpx
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://thedyrt.com/api/v6/locations/search-results"
HEADERS = {"User-Agent": "Mozilla/5.0"}

async def fetch_page(page):
    params = {
        "filter[search][drive_time]": "any",
        "filter[search][air_quality]": "any",
        "filter[search][electric_amperage]": "any",
        "filter[search][max_vehicle_length]": "any",
        "filter[search][price]": "any",
        "filter[search][rating]": "any",
        "filter[search][region]": "any",
        "sort": "recommended",
        "page[number]": page,
        "page[size]": 500,
    }

    logger.info(f"Fetching page: {page}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params, headers=HEADERS)
            response.raise_for_status()
            logger.info(f"Successfully fetched page: {page}")
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                logger.warning(f"Page {page} returned a 500 error. Skipping...")
                return None  # Indicate failure for this page
            else:
                logger.error(f"HTTP error occurred while fetching page {page}: {e}")
                raise  # Re-raise other HTTP errors

async def fetch_all_pages():
    tasks = [fetch_page(page) for page in range(1, 23)] 
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Filter out failed pages and log errors
    valid_results = [result for result in results if result is not None]
    
    logger.info(f"Successfully fetched {len(valid_results)} pages.")
    
    return valid_results
