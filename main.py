from browser import Browser
import json
import time
import re
from url import urls
from database import ReviewDatabase


OUTPUT_FILE = "reviews.json"


def clean_review_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text).strip()

    owner_patterns = [
        r"\bResponse from the owner\b.*$",
        r"\bOwner response\b.*$",
        r"\bResponse from owner\b.*$",
    ]

    for pattern in owner_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

    text = re.sub(
        r"(?:\s*[]\s*)?Like\s+(?:\s*)?Share\s*$",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    text = re.sub(
        r"\s*Like\s*$",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    text = re.sub(
        r"\s*Share\s*$",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    text = text.replace("", " ")
    text = re.sub(r"(?:\s*)+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def scrape_reviews(browser, url, source):
    separator = "&" if "?" in url else "?"
    url += separator + "hl=en"

    print()
    print("[+] Navigating to:")
    print(url)

    browser.goto(url, wait=7)

    print("[+] Looking for Reviews...")

    result = browser.evaluate("""
    (() => {

        const elements = [...document.querySelectorAll('*')];

        const exact = elements.find(el => {

            const text =
                (el.innerText || '').trim();

            return (
                text === 'Reviews' ||
                text === 'reviews'
            );

        });

        if (exact) {

            exact.click();

            return {
                clicked: true,
                type: 'exact'
            };

        }

        const candidates = elements.filter(el => {

            const text =
                (el.innerText || '').trim();

            const aria =
                (
                    el.getAttribute('aria-label') ||
                    ''
                ).trim();

            return (
                text === 'Reviews' ||
                text.includes('Reviews') ||
                aria.includes('Reviews')
            );

        });

        if (candidates.length) {

            const preferred =
                candidates.find(el => {

                    const role =
                        el.getAttribute('role');

                    return (
                        role === 'tab' ||
                        role === 'button'
                    );

                }) || candidates[0];

            preferred.click();

            return {
                clicked: true,
                type: 'fallback'
            };

        }

        return {
            clicked: false
        };

    })()
    """)

    try:
        print(
            "[+] Reviews click:",
            result["result"]["value"]
        )
    except Exception:
        pass

    time.sleep(4)

    print("[+] Loading reviews...")

    previous_height = 0
    unchanged_count = 0

    MAX_SCROLLS = 100000

    for i in range(MAX_SCROLLS):

        result = browser.evaluate("""
        (() => {

            const elements = [
                ...document.querySelectorAll('div')
            ];

            const scrollables =
                elements.filter(el => {

                    const style =
                        getComputedStyle(el);

                    return (
                        el.scrollHeight >
                        el.clientHeight + 100
                    ) && (
                        style.overflowY === 'auto' ||
                        style.overflowY === 'scroll'
                    );

                });

            let containers =
                scrollables.filter(el => {

                    return (
                        el.querySelector(
                            'div.jftiEf'
                        ) !== null
                    );

                });

            containers.sort(
                (a, b) =>
                    b.scrollHeight -
                    a.scrollHeight
            );

            let container =
                containers[0];

            if (!container) {

                containers =
                    scrollables.filter(el => {

                        const text =
                            el.innerText || '';

                        return (
                            text.includes(
                                'Response from the owner'
                            ) ||
                            text.includes(
                                'Order type'
                            ) ||
                            text.includes(
                                'Local Guide'
                            ) ||
                            text.includes(
                                'reviews'
                            )
                        );

                    });

                containers.sort(
                    (a, b) =>
                        b.scrollHeight -
                        a.scrollHeight
                );

                container =
                    containers[0];

            }

            if (!container) {

                return {
                    found: false,
                    height: 0,
                    top: 0
                };

            }

            container.scrollTop =
                container.scrollHeight;

            return {
                found: true,
                height: container.scrollHeight,
                top: container.scrollTop
            };

        })()
        """)

        try:
            info = result["result"]["value"]
            height = info.get("height", 0)
        except Exception:
            height = 0

        print(
            f"[+] Scroll {i + 1}/{MAX_SCROLLS} "
            f"| height={height}"
        )

        time.sleep(1.5)

        if height == previous_height:
            unchanged_count += 1
        else:
            unchanged_count = 0

        previous_height = height

        if unchanged_count >= 7:
            print(
                "[+] Review list appears fully loaded."
            )
            break

    print("[+] Expanding review text...")

    for pass_number in range(15):

        result = browser.evaluate("""
        (() => {

            let clicked = 0;

            const cards = [
                ...document.querySelectorAll(
                    'div.jftiEf'
                )
            ];

            for (const card of cards) {

                const elements = [
                    ...card.querySelectorAll('*')
                ];

                for (const element of elements) {

                    const text =
                        (
                            element.innerText ||
                            ''
                        ).trim();

                    const aria =
                        (
                            element.getAttribute(
                                'aria-label'
                            ) || ''
                        ).trim();

                    if (
                        text === 'More' ||
                        text === 'more' ||
                        aria === 'More' ||
                        aria === 'more'
                    ) {

                        if (
                            element.innerText &&
                            element.innerText.trim()
                                .length > 20
                        ) {
                            continue;
                        }

                        try {
                            element.click();
                            clicked++;
                        } catch (e) {}

                    }

                }

            }

            return {
                clicked: clicked
            };

        })()
        """)

        try:
            clicked = result["result"]["value"].get(
                "clicked",
                0
            )
        except Exception:
            clicked = 0

        print(
            f"[+] Expansion pass "
            f"{pass_number + 1}: "
            f"{clicked} clicked"
        )

        time.sleep(1)

        if clicked == 0:
            break

    time.sleep(2)

    print("[+] Extracting reviews...")

    result = browser.evaluate("""
    (() => {
        const reviews = [];
        const cards = [...document.querySelectorAll('div.jftiEf')];
        const fields = [
            ['meal_type', ['Meal type']],
            ['price_per_person', ['Price per person']],
            ['atmosphere', ['Atmosphere']],
            ['parking_options', ['Parking options', 'Parking']],
            ['recommended_dishes', ['Recommended dishes']],
            ['food', ['Food']],
            ['service', ['Service']],
            ['noise_level', ['Noise level']],
            ['wait_time', ['Wait time']],
            ['seating', ['Seating']],
            ['accessibility', ['Accessibility']],
            ['reservations', ['Reservations']],
            ['payment_options', ['Payment options']],
            ['kid_friendliness', ['Kid-friendliness', 'Kid friendliness']],
            ['dietary_restrictions', ['Dietary restrictions']],
            ['popular_times', ['Popular times']]
        ];

        const normalize = value =>
            (value || '').replace(/\\s+/g, ' ').trim();

        const escapeRegExp = value =>
            value.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');

        const getFieldValue = (card, labels) => {
            const elements = [...card.querySelectorAll('*')];
            for (const label of labels) {
                const labelRegex = new RegExp('^' + escapeRegExp(label) + '\\s*:?', 'i');
                const exactRegex = new RegExp('^' + escapeRegExp(label) + '\\s*:?[\\s]*$', 'i');
                for (const el of elements) {
                    const text = normalize(el.innerText);
                    if (!text) continue;
                    if (exactRegex.test(text)) {
                        const parent = el.parentElement;
                        if (parent) {
                            const parentText = normalize(parent.innerText);
                            const remainder = normalize(parentText.replace(new RegExp('^' + escapeRegExp(label) + '\\s*:?\\s*', 'i'), ''));
                            if (remainder && remainder !== text) return remainder;
                            const siblings = [...parent.children];
                            const index = siblings.indexOf(el);
                            if (index >= 0 && siblings[index + 1]) {
                                const siblingText = normalize(siblings[index + 1].innerText);
                                if (siblingText) return siblingText;
                            }
                        }
                    }
                    if (labelRegex.test(text)) {
                        const value = normalize(text.replace(labelRegex, ''));
                        if (value) return value;
                    }
                }
            }
            return '';
        };

        const isOwnerResponse = element => {
            let node = element;
            for (let level = 0; level < 8 && node; level++) {
                const nodeText = normalize(node.innerText).toLowerCase();
                const nodeClass = String(node.className || '').toLowerCase();
                const nodeAria = String(node.getAttribute('aria-label') || '').toLowerCase();
                if (
                    nodeText.includes('response from the owner') ||
                    nodeClass.includes('owner') ||
                    nodeClass.includes('response') ||
                    nodeAria.includes('owner response')
                ) return true;
                node = node.parentElement;
            }
            return false;
        };

        for (const card of cards) {
            const nameEl = card.querySelector('.d4r55');
            const name = nameEl ? normalize(nameEl.innerText) : '';
            if (!name) continue;

            let rating = '';
            const ratingCandidates = [
                ...card.querySelectorAll('[role="img"]'),
                ...card.querySelectorAll('[aria-label*="star" i]')
            ];
            for (const element of ratingCandidates) {
                const aria = normalize(element.getAttribute('aria-label'));
                const match = aria.match(/([1-5])\\s*stars?/i);
                if (match) {
                    rating = match[1] + ' stars';
                    break;
                }
            }

            let date = '';
            const dateEl = card.querySelector('.rsqaWe');
            if (dateEl) date = normalize(dateEl.innerText);

            const attributes = {};
            for (const [key, labels] of fields) {
                attributes[key] = getFieldValue(card, labels);
            }

            const clone = card.cloneNode(true);
            const allCloneElements = [...clone.querySelectorAll('*')];

            for (const element of allCloneElements) {
                const txt = normalize(element.innerText).toLowerCase();
                const aria = normalize(element.getAttribute('aria-label')).toLowerCase();
                if (
                    txt.startsWith('response from the owner') ||
                    aria.includes('response from the owner') ||
                    /^order type\\s*:?/i.test(txt)
                ) element.remove();
            }

            for (const [, labels] of fields) {
                for (const label of labels) {
                    const elements = [...clone.querySelectorAll('*')];
                    const exactRegex = new RegExp('^' + escapeRegExp(label) + '\\s*:?[\\s]*$', 'i');
                    const startsRegex = new RegExp('^' + escapeRegExp(label) + '\\s*:', 'i');
                    for (const element of elements) {
                        const txt = normalize(element.innerText);
                        if (exactRegex.test(txt) || startsRegex.test(txt)) element.remove();
                    }
                }
            }

            clone.querySelectorAll('.d4r55, .rsqaWe, button, [role="button"], img, svg').forEach(el => el.remove());

            let cardText = normalize(clone.innerText);
            if (name) cardText = cardText.replace(new RegExp('^' + escapeRegExp(name) + '\\s*', 'i'), '');
            if (rating) cardText = cardText.replace(new RegExp(escapeRegExp(rating), 'ig'), '');
            if (date) cardText = cardText.replace(new RegExp(escapeRegExp(date), 'ig'), '');
            cardText = cardText.replace(/(?:\\s*)+/g, ' ');
            cardText = cardText.replace(/(^|\\s)(Like|Share|More)(?=\\s|$)/gi, ' ');
            cardText = cardText.replace(/\\bResponse from the owner\\b.*$/i, '');
            cardText = cardText.replace(/\\bOwner response\\b.*$/i, '');
            cardText = normalize(cardText);

            const review = {
                name,
                rating,
                date,
                meal_type: attributes.meal_type,
                price_per_person: attributes.price_per_person,
                atmosphere: attributes.atmosphere,
                parking_options: attributes.parking_options,
                recommended_dishes: attributes.recommended_dishes,
                food: attributes.food,
                service: attributes.service,
                noise_level: attributes.noise_level,
                wait_time: attributes.wait_time,
                seating: attributes.seating,
                accessibility: attributes.accessibility,
                reservations: attributes.reservations,
                payment_options: attributes.payment_options,
                kid_friendliness: attributes.kid_friendliness,
                dietary_restrictions: attributes.dietary_restrictions,
                popular_times: attributes.popular_times,
                text: cardText
            };

            reviews.push(review);
        }

        const unique = [];
        const seen = new Set();
        for (const review of reviews) {
            const key = JSON.stringify(review);
            if (seen.has(key)) continue;
            seen.add(key);
            unique.push(review);
        }

        return { cards: cards.length, reviews: unique };
    })()
    """)

    data = result["result"]["value"]

    reviews = data.get(
        "reviews",
        []
    )

    cleaned_reviews = []

    for review in reviews:

        text = clean_review_text(
            review.get(
                "text",
                ""
            )
        )

        cleaned_reviews.append({
            "source": source,
            "name": review.get("name", ""),
            "rating": review.get("rating", ""),
            "date": review.get("date", ""),
            "meal_type": review.get("meal_type", ""),
            "price_per_person": review.get("price_per_person", ""),
            "atmosphere": review.get("atmosphere", ""),
            "parking_options": review.get("parking_options", ""),
            "recommended_dishes": review.get("recommended_dishes", ""),
            "food": review.get("food", ""),
            "service": review.get("service", ""),
            "noise_level": review.get("noise_level", ""),
            "wait_time": review.get("wait_time", ""),
            "seating": review.get("seating", ""),
            "accessibility": review.get("accessibility", ""),
            "reservations": review.get("reservations", ""),
            "payment_options": review.get("payment_options", ""),
            "kid_friendliness": review.get("kid_friendliness", ""),
            "dietary_restrictions": review.get("dietary_restrictions", ""),
            "popular_times": review.get("popular_times", ""),
            "text": text
        })

    final_reviews = []

    seen = set()

    for review in cleaned_reviews:

        key = json.dumps(review, ensure_ascii=False, sort_keys=True)

        if key in seen:
            continue

        seen.add(key)

        final_reviews.append(review)

    print()
    print("========================================")
    print(
        "REVIEW CARDS:",
        data.get(
            "cards",
            0
        )
    )
    print(
        "CLEAN REVIEWS:",
        len(final_reviews)
    )
    print("========================================")

    for i, review in enumerate(
        final_reviews,
        1
    ):

        print()

        print(
            f"--- REVIEW {i} ---"
        )

        print(
            "Name   :",
            review["name"]
        )

        print(
            "Rating :",
            review["rating"]
        )

        print(
            "Date   :",
            review["date"]
        )

        print(
            "Text   :",
            review["text"]
        )

    return final_reviews


def main():

    browser = Browser()

    all_reviews = []

    try:

        browser.start()

        print("[+] Chrome started")

        if not urls:
            print(
                "[!] No URLs found in url.py."
            )
            return

        print(
            f"[+] Found {len(urls)} URLs."
        )

        for index, (source, url) in enumerate(
            urls.items(),
            1
        ):

            print()
            print(
                "########################################"
            )
            print(
                f"URL {index}/{len(urls)}"
            )
            print(
                "########################################"
            )

            try:

                reviews = scrape_reviews(
                    browser,
                    url,
                    source
                )

                all_reviews.extend(reviews)

                print(
                    f"[+] URL {index} complete: "
                    f"{len(reviews)} reviews"
                )

            except Exception as e:

                print(
                    f"[!] Error processing URL "
                    f"{index}: {e}"
                )

                continue

        final_reviews = []

        seen = set()

        for review in all_reviews:

            key = (
                review["name"],
                review["rating"],
                review["date"],
                review["text"]
            )

            if key in seen:
                continue

            seen.add(key)

            final_reviews.append(review)

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                final_reviews,
                f,
                indent=2,
                ensure_ascii=False
            )

        print()
        print(
            "========================================"
        )
        print(
            f"[+] Finished all {len(urls)} URLs"
        )
        print(
            f"[+] Total unique reviews: "
            f"{len(final_reviews)}"
        )
        print(
            f"[+] Saved everything to {OUTPUT_FILE}"
        )
        print(
            "========================================"
        )

        input(
            "\nPress ENTER to close Chrome..."
        )

    finally:

        browser.close()


main()


db = ReviewDatabase("reviews.db")

try:
    inserted, skipped = db.import_json("reviews.json")

    print(
        f"[+] Database: inserted {inserted}, skipped {skipped}"
    )

finally:
    db.close()