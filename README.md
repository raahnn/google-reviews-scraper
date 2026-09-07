# Google Reviews Scraper

A Python-based scraper for extracting reviews and review details from Google Maps.

The scraper takes Google Maps place URLs and extracts information such as reviewer names, ratings, dates, review text, and the additional questions/details Google provides for certain types of businesses, such as restaurants.

The scraped data is saved in **JSON format**, with optional **SQLite database** storage.

## Features

* Scrape reviews from Google Maps
* Extract reviewer names
* Extract review ratings
* Extract review dates
* Extract review text
* Extract Google Maps' additional/default review questions and their answers when available
* Save scraped results as JSON
* Optional SQLite database storage
* Supports multiple Google Maps places through `url.py`
* Uses an installed Chromium-based browser for scraping

## Requirements

Before installing the project, make sure you have the following:

* **Python 3.14 or higher**
* A **Chromium-based browser**, such as:

  * Google Chrome
  * Brave
  * Microsoft Edge
  * Chromium
  * or another Chromium-based browser

The browser must be installed on the device because the scraper uses it to access Google Maps.

## Installation

Clone or download this repository and open a terminal/Command Prompt inside the project folder.

Install the required Python packages using:

```bash
pip install -r r.txt
```

SQLite support is included through the Python dependencies installed from `r.txt`, so no separate SQLite installation is required.

## Adding Google Maps Places

Google Maps URLs are provided through `url.py`.

Open `url.py` and add your places using the following format:

```python
"Place Name": "Google Maps Link"
```

For example:

```python
urls = {
    "place 1": "https://www.google.com/maps/...",
    "place 2": "https://www.google.com/maps/..."
}
```

The **name of the place goes on the left side of the colon**, and the **Google Maps URL goes on the right side**.

You can add multiple places to scrape.

## Running the Scraper

After adding your Google Maps URLs, open Command Prompt/Terminal in the project folder and run:

```bash
py main.py
```

The scraper will then process the places provided in `url.py`.

## Output

The scraper produces JSON data containing the information collected from the reviews.

A typical review object looks like this:

```json
{
    "source": "restaurant",
    "name": "name",
    "rating": "5 stars",
    "date": "X months ago",
    "meal_type": "Lunch",
    "price_per_person": "",
    "atmosphere": "1",
    "parking_options": "",
    "recommended_dishes": "",
    "food": "1",
    "service": "1",
    "noise_level": "",
    "wait_time": "",
    "seating": "",
    "accessibility": "",
    "reservations": "",
    "payment_options": "",
    "kid_friendliness": "",
    "dietary_restrictions": "",
    "popular_times": "",
    "text": "review example"
}
```

### Available Fields

Depending on what Google Maps provides for a particular review, the scraper can return fields such as:

| Field                  | Description                              |
| ---------------------- | ---------------------------------------- |
| `source`               | Type/category of the place               |
| `name`                 | Reviewer name                            |
| `rating`               | Review rating                            |
| `date`                 | Date/time period shown by Google         |
| `text`                 | Review text                              |
| `meal_type`            | Meal type, when available                |
| `price_per_person`     | Price information, when available        |
| `atmosphere`           | Atmosphere rating/answer, when available |
| `parking_options`      | Parking information                      |
| `recommended_dishes`   | Recommended dishes                       |
| `food`                 | Food rating/answer                       |
| `service`              | Service rating/answer                    |
| `noise_level`          | Noise level                              |
| `wait_time`            | Wait time                                |
| `seating`              | Seating information                      |
| `accessibility`        | Accessibility information                |
| `reservations`         | Reservation information                  |
| `payment_options`      | Payment information                      |
| `kid_friendliness`     | Kid-friendliness information             |
| `dietary_restrictions` | Dietary restriction information          |
| `popular_times`        | Popular-times information                |

Not every field will be populated for every review. If Google does not provide an answer for a particular question, the corresponding field may be empty.

## Google Maps Default Review Questions

For some businesses, Google Maps displays additional questions/details when users leave a review.

The scraper attempts to collect these as separate fields when they are available.

These fields depend on the information Google Maps makes available for that particular review.

## SQLite Database

The project also supports saving the scraped data to a **SQLite database**.

The SQLite-related code is located near the end of `main.py`.

By default, you can use the JSON output. If you want to store the scraped reviews in SQLite, uncomment the relevant SQLite/database lines near the end of `main.py`.

SQLite does not require a separate database server and is included through the project's Python dependencies.

## Google Maps Sign-In Issue

Sometimes Google Maps may require you to sign in before allowing reviews to be viewed.

If the scraper does **not** retrieve reviews from a particular Google Maps link, this may be because Google has requested a sign-in for that page.

### Recommended solution

**Do not use a reviews-section link as your first approach.**

First, try the normal Google Maps place link.

If reviews cannot be retrieved because Google is asking for a sign-in, open the Google Maps page manually, navigate to its **Reviews** section, and copy the URL for that reviews section.

Then replace the original URL in `url.py` with the reviews-section URL and run the scraper again.

For example:

```python
urls = {
    "Place Name": "REVIEWS_SECTION_URL"
}
```

This is only a fallback when the normal Google Maps place URL does not work.

## Example Workflow

### 1. Install the dependencies

```bash
pip install -r r.txt
```

### 2. Add a Google Maps URL

Edit `url.py`:

```python
urls = {
    "My Restaurant": "https://www.google.com/maps/..."
}
```

### 3. Run the scraper

```bash
py main.py
```

### 4. Check the JSON output

The scraped reviews will be saved as JSON containing the available review information and Google Maps' additional review-question data.

### 5. Optional: Enable SQLite

If you also want database storage, uncomment the SQLite-related code near the end of `main.py` and run:

```bash
py main.py
```

## Project Structure

A basic project structure looks like:

```text
google-reviews-scraper/
│
├── main.py
├── url.py
├── r.txt
└── ...
```

### `main.py`

The main scraper script. Run this file to start scraping.

### `url.py`

Contains the Google Maps places/URLs that you want to scrape.

### `r.txt`

Contains the Python dependencies required by the project.

## Notes

* Google Maps can change its website structure at any time, which may affect scraping.
* The information available for each review depends on what Google Maps displays.
* Some review-question fields may be empty.
* Google may occasionally require sign-in or otherwise restrict access to reviews.
* A Chromium-based browser must be installed on the machine running the scraper.
* Use the reviews-section URL only as a fallback when the normal Google Maps place URL cannot retrieve reviews.

## Quick Start

```bash
pip install -r r.txt
py main.py
```

That's it. Add your Google Maps URLs to `url.py` and run `main.py`.

