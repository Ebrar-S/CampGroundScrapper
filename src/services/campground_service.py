import logging
from datetime import datetime
from typing import List, Optional
from src.models.campground import Campground
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.database.connection import engine
from src.models import db_model

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("campground_logger")

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

def convert_data_to_campground(item_data: dict) -> Campground:
    """
    Converts the raw campground data into a valid Campground object.

    Args:
        item_data: A dictionary representing the raw data (e.g., from an API).

    Returns:
        A Campground object created from the raw data.
    """
    attributes = item_data.get('attributes', {})
    mapped_item = {
        "id": item_data.get('id'),
        "type": item_data.get('type'),
        "links": {
            "self": item_data.get('links', {}).get('self')
        },
        "name": attributes.get('name'),
        "latitude": attributes.get('latitude'),
        "longitude": attributes.get('longitude'),
        "region-name": attributes.get('region-name'),
        "administrative-area": attributes.get('administrative-area'),
        "nearest-city-name": attributes.get('nearest-city-name'),
        "accommodation-type-names": attributes.get('accommodation-type-names', []),
        "bookable": attributes.get('bookable', False),
        "camper-types": attributes.get('camper-types', []),
        "operator": attributes.get('operator'),
        "photo-url": attributes.get('photo-url'),
        "photo-urls": attributes.get('photo-urls', []),
        "photos-count": attributes.get('photos-count', 0),
        "rating": attributes.get('rating'),
        "reviews-count": attributes.get('reviews-count', 0),
        "slug": attributes.get('slug'),
        "price-low": float(attributes.get('price-low', '0.00')) if attributes.get('price-low') else None,
        "price-high": float(attributes.get('price-high', '0.00')) if attributes.get('price-high') else None,
        "availability-updated-at": datetime.strptime(attributes.get('availability-updated-at', ''), '%Y-%m-%dT%H:%M:%S.%fZ') if attributes.get('availability-updated-at') else None
    }
    return Campground.model_validate(mapped_item)

def validate_data(campground_data: dict) -> Optional[List[Campground]]:
    """
    Validates the campground data using the Pydantic model.

    Args:
        campground_data (dict): The dictionary containing campground data.

    Returns:
        Optional[List[Campground]]: A list of validated Campground objects or None if validation fails.
    """
    validated_campgrounds = []
    for item in campground_data.get("data", []):
        try:
            campground = convert_data_to_campground(item)
            validated_campgrounds.append(campground)
        except ValidationError as e:
            logger.warning(f"Validation error for item: {item.get('id', 'unknown')}\n{e}")
        except Exception as e:
            logger.error(f"Unexpected error for item: {item.get('id', 'unknown')}\n{e}")

    if validated_campgrounds:
        logger.info(f"Successfully validated {len(validated_campgrounds)} campgrounds.")
        return validated_campgrounds
    else:
        logger.warning("No valid campgrounds found.")
        return None

def save_update_to_db(campgrounds: List[Campground]):
    """
    Saves or updates the validated campground data in the database.
    
    Args:
        campgrounds (List[Campground]): A list of validated Campground objects.
    """
    try:
        for campground in campgrounds:
            photo_urls_as_str = [str(url) for url in campground.photo_urls]
            links_as_dict = {"self": str(campground.links.self)}

            existing_campground = session.query(db_model.Campground).filter_by(id=campground.id).first()

            if existing_campground:
                existing_campground.type = campground.type
                existing_campground.links = links_as_dict
                existing_campground.name = campground.name
                existing_campground.latitude = campground.latitude
                existing_campground.longitude = campground.longitude
                existing_campground.region_name = campground.region_name
                existing_campground.administrative_area = campground.administrative_area
                existing_campground.nearest_city_name = campground.nearest_city_name
                existing_campground.accommodation_type_names = campground.accommodation_type_names
                existing_campground.bookable = campground.bookable
                existing_campground.camper_types = campground.camper_types
                existing_campground.operator = campground.operator
                existing_campground.photo_url = str(campground.photo_url) if campground.photo_url else None
                existing_campground.photo_urls = photo_urls_as_str
                existing_campground.photos_count = campground.photos_count
                existing_campground.rating = campground.rating
                existing_campground.reviews_count = campground.reviews_count
                existing_campground.slug = campground.slug
                existing_campground.price_low = campground.price_low
                existing_campground.price_high = campground.price_high
                existing_campground.availability_updated_at = campground.availability_updated_at
                logger.info(f"Updated record: {campground.id}")
            else:
                db_campground = db_model.Campground(
                    id=campground.id,
                    type=campground.type,
                    links=links_as_dict,
                    name=campground.name,
                    latitude=campground.latitude,
                    longitude=campground.longitude,
                    region_name=campground.region_name,
                    administrative_area=campground.administrative_area,
                    nearest_city_name=campground.nearest_city_name,
                    accommodation_type_names=campground.accommodation_type_names,
                    bookable=campground.bookable,
                    camper_types=campground.camper_types,
                    operator=campground.operator,
                    photo_url=str(campground.photo_url) if campground.photo_url else None,
                    photo_urls=photo_urls_as_str,
                    photos_count=campground.photos_count,
                    rating=campground.rating,
                    reviews_count=campground.reviews_count,
                    slug=campground.slug,
                    price_low=campground.price_low,
                    price_high=campground.price_high,
                    availability_updated_at=campground.availability_updated_at
                )
                session.add(db_campground)
                logger.info(f"Inserted new record: {campground.id}")

        session.commit()
        logger.info("All changes committed successfully.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        session.rollback()
    except Exception as e:
        logger.error(f"Unexpected error while saving data: {e}")
        session.rollback()
