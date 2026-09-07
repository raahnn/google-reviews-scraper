import sqlite3
import json
import threading

from cleaner import clean_ascii


class ReviewDatabase:

    def __init__(self, database_path: str):
        self.database_path = database_path

        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False
        )

        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous=NORMAL;")

        self.lock = threading.Lock()

        self._create_table()

    def _create_table(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reviewer TEXT NOT NULL,
                review TEXT NOT NULL,
                stars INTEGER NOT NULL
                    CHECK (stars IN (4, 5)),
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL DEFAULT '',
                price_per_person TEXT NOT NULL DEFAULT '',
                atmosphere TEXT NOT NULL DEFAULT '',
                parking_options TEXT NOT NULL DEFAULT '',
                recommended_dishes TEXT NOT NULL DEFAULT '',
                food TEXT NOT NULL DEFAULT '',
                service TEXT NOT NULL DEFAULT '',
                noise_level TEXT NOT NULL DEFAULT '',
                wait_time TEXT NOT NULL DEFAULT '',
                seating TEXT NOT NULL DEFAULT '',
                accessibility TEXT NOT NULL DEFAULT '',
                reservations TEXT NOT NULL DEFAULT '',
                payment_options TEXT NOT NULL DEFAULT '',
                kid_friendliness TEXT NOT NULL DEFAULT '',
                dietary_restrictions TEXT NOT NULL DEFAULT '',
                popular_times TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL,
                UNIQUE (reviewer, date)
            )
            """
        )

        columns = {
            "date": "TEXT NOT NULL DEFAULT ''",
            "meal_type": "TEXT NOT NULL DEFAULT ''",
            "price_per_person": "TEXT NOT NULL DEFAULT ''",
            "atmosphere": "TEXT NOT NULL DEFAULT ''",
            "parking_options": "TEXT NOT NULL DEFAULT ''",
            "recommended_dishes": "TEXT NOT NULL DEFAULT ''",
            "food": "TEXT NOT NULL DEFAULT ''",
            "service": "TEXT NOT NULL DEFAULT ''",
            "noise_level": "TEXT NOT NULL DEFAULT ''",
            "wait_time": "TEXT NOT NULL DEFAULT ''",
            "seating": "TEXT NOT NULL DEFAULT ''",
            "accessibility": "TEXT NOT NULL DEFAULT ''",
            "reservations": "TEXT NOT NULL DEFAULT ''",
            "payment_options": "TEXT NOT NULL DEFAULT ''",
            "kid_friendliness": "TEXT NOT NULL DEFAULT ''",
            "dietary_restrictions": "TEXT NOT NULL DEFAULT ''",
            "popular_times": "TEXT NOT NULL DEFAULT ''",
            "source": "TEXT NOT NULL DEFAULT ''"
        }

        existing_columns = {
            row[1]
            for row in self.connection.execute(
                "PRAGMA table_info(review)"
            ).fetchall()
        }

        for column, definition in columns.items():
            if column not in existing_columns:
                self.connection.execute(
                    f"ALTER TABLE review ADD COLUMN {column} {definition}"
                )

        self.connection.execute(
            """
            DELETE FROM review
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM review
                GROUP BY review
            )
            """
        )

        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_review_unique_review
            ON review(review)
            """
        )

        self.connection.commit()

    def insert_review(
        self,
        reviewer: str,
        review: str,
        stars: int,
        date: str,
        meal_type: str = "",
        price_per_person: str = "",
        atmosphere: str = "",
        parking_options: str = "",
        recommended_dishes: str = "",
        food: str = "",
        service: str = "",
        noise_level: str = "",
        wait_time: str = "",
        seating: str = "",
        accessibility: str = "",
        reservations: str = "",
        payment_options: str = "",
        kid_friendliness: str = "",
        dietary_restrictions: str = "",
        popular_times: str = "",
        source: str = ""
    ):

        if stars not in (4, 5):
            return False

        reviewer = clean_ascii(reviewer)
        review = clean_ascii(review)
        meal_type = clean_ascii(meal_type)
        date = date
        price_per_person = price_per_person
        atmosphere = clean_ascii(atmosphere)
        parking_options = clean_ascii(parking_options)
        recommended_dishes = clean_ascii(recommended_dishes)
        food = clean_ascii(food)
        service = clean_ascii(service)
        noise_level = clean_ascii(noise_level)
        wait_time = clean_ascii(wait_time)
        seating = clean_ascii(seating)
        accessibility = clean_ascii(accessibility)
        reservations = clean_ascii(reservations)
        payment_options = clean_ascii(payment_options)
        kid_friendliness = clean_ascii(kid_friendliness)
        dietary_restrictions = clean_ascii(dietary_restrictions)
        popular_times = clean_ascii(popular_times)
        source = source

        if not reviewer or not review:
            return False

        with self.lock:

            cursor = self.connection.execute(
                """
                INSERT OR IGNORE INTO review (
                    reviewer,
                    review,
                    stars,
                    date,
                    meal_type,
                    price_per_person,
                    atmosphere,
                    parking_options,
                    recommended_dishes,
                    food,
                    service,
                    noise_level,
                    wait_time,
                    seating,
                    accessibility,
                    reservations,
                    payment_options,
                    kid_friendliness,
                    dietary_restrictions,
                    popular_times,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reviewer,
                    review,
                    stars,
                    date,
                    meal_type,
                    price_per_person,
                    atmosphere,
                    parking_options,
                    recommended_dishes,
                    food,
                    service,
                    noise_level,
                    wait_time,
                    seating,
                    accessibility,
                    reservations,
                    payment_options,
                    kid_friendliness,
                    dietary_restrictions,
                    popular_times,
                    source
                )
            )

            self.connection.commit()

        return cursor.rowcount > 0

    def import_json(self, json_path: str):

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as f:

            reviews = json.load(f)

        inserted = 0
        skipped = 0

        for item in reviews:

            reviewer = item.get("name", "")
            review = item.get("text", "")
            date = item.get("date", "")
            meal_type = item.get("meal_type", "")
            price_per_person = item.get("price_per_person", "")
            atmosphere = item.get("atmosphere", "")
            parking_options = item.get("parking_options", "")
            recommended_dishes = item.get("recommended_dishes", "")
            food = item.get("food", "")
            service = item.get("service", "")
            noise_level = item.get("noise_level", "")
            wait_time = item.get("wait_time", "")
            seating = item.get("seating", "")
            accessibility = item.get("accessibility", "")
            reservations = item.get("reservations", "")
            payment_options = item.get("payment_options", "")
            kid_friendliness = item.get("kid_friendliness", "")
            dietary_restrictions = item.get("dietary_restrictions", "")
            popular_times = item.get("popular_times", "")
            source = item.get("source", "")

            rating = item.get(
                "rating",
                ""
            )

            try:
                stars = int(
                    str(rating)
                    .strip()
                    .split()[0]
                )
            except (ValueError, IndexError):
                skipped += 1
                continue

            if self.insert_review(
                reviewer,
                review,
                stars,
                date,
                meal_type,
                price_per_person,
                atmosphere,
                parking_options,
                recommended_dishes,
                food,
                service,
                noise_level,
                wait_time,
                seating,
                accessibility,
                reservations,
                payment_options,
                kid_friendliness,
                dietary_restrictions,
                popular_times,
                source
            ):
                inserted += 1
            else:
                skipped += 1

        return inserted, skipped

    def close(self):
        self.connection.close()


def main():

    database = ReviewDatabase(
        "reviews.db"
    )

    try:

        inserted, skipped = database.import_json(
            "reviews.json"
        )

        print(
            f"[+] Inserted: {inserted}"
        )

        print(
            f"[+] Skipped: {skipped}"
        )

    finally:

        database.close()


if __name__ == "__main__":
    main()