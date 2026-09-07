from zealium import Zealium
import time


class Browser:
    def __init__(self):
        self.zealium = Zealium(
            browser="chrome",
            stealth_level="normal",
            timeout=20,
        )

        self.tab = None
    """ts for opening the browser"""
    def start(self):
        print("[+] Starting Chromium...")

        self.zealium.launch()
        self.tab = self.zealium.tab

        print("[+] Chromium started")

    def goto(self, url, wait=5):
        print(f"[+] Navigating to: {url}")

        self.tab.Page.navigate(
            url=url,
            _timeout=30,
        )

        time.sleep(wait)

    """this for js"""
    def evaluate(self, javascript):

        result = self.tab.Runtime.evaluate(
            expression=javascript,
            returnByValue=True,
            awaitPromise=True,
        )

        return result

    def close(self):
        print("[+] Closing Chromium...")
        self.zealium.close()