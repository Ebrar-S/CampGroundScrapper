import logging
import multiprocessing
from flask import Flask, jsonify
from src.scheduler.scheduler import scheduled_scraper

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

is_scraper_running = False
scraper_process = None

def run_scraper():
    global is_scraper_running
    try:
        logger.info("Scraper started...")
        scheduled_scraper()
    except Exception as e:
        logger.error(f"Error in scraper: {e}")
    finally:
        is_scraper_running = False
        logger.info("Scraper stopped.")

@app.route("/", methods=["GET"])
def home():
    return """
        <h1>Welcome to the Campground Scraping API...</h1>
        <p>You can start the scraper by going to the <a href="/start-scraper">start-scraper</a> route.</p>
    """

@app.route("/start-scraper", methods=["GET"])
def start_scraper():
    global is_scraper_running, scraper_process

    if is_scraper_running:
        return """
        <h1>Scraper is already running.</h1>
        <p>You can stop the scraper by going to the <a href="/stop-scraper">stop-scraper</a> route.</p>
        <p>Or you can go back to the <a href="/">home</a> page.</p>
    """, 200

    is_scraper_running = True
    scraper_process = multiprocessing.Process(target=run_scraper)
    scraper_process.start()

    return """
        <h1>Scraper has been started.</h1>
        <p>You can stop the scraper by going to the <a href="/stop-scraper">stop-scraper</a> route.</p>
        <p>Or you can go back to the <a href="/">home</a> page.</p>
    """

@app.route("/stop-scraper", methods=["GET"])
def stop_scraper():
    global is_scraper_running, scraper_process

    if not is_scraper_running:
        return """
        <h1>Scraper is not running.</h1>
        <p>You can start the scraper again by going to the <a href="/start-scraper">start-scraper</a> route.</p>
        <p>Or you can go back to the <a href="/">home</a> page.</p>
    """, 200

    scraper_process.terminate()
    scraper_process.join()

    is_scraper_running = False
    return """
        <h1>Scraper has been stopped.</h1>
        <p>You can start the scraper again by going to the <a href="/start-scraper">start-scraper</a> route.</p>
        <p>Or you can go back to the <a href="/">home</a> page.</p>
    """

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"is_scraper_running": is_scraper_running})

if __name__ == "__main__":
    logger.info("Starting the Flask app...")
    app.run(host="0.0.0.0", port=5000)
