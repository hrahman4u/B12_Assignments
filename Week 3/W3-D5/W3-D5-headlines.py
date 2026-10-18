import requests
from bs4 import BeautifulSoup

URL = "https://www.bbc.com/news"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_top_headlines():
    try:
        # 1. Fetch the webpage with a browser User-Agent
        response = requests.get(URL, headers=HEADERS, timeout=10)

        # 2. Check the HTTP status code before parsing
        if response.status_code != 200:
            print(f"Failed to fetch page. HTTP Status: {response.status_code}")
            return

        # 3. Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # 4. Target headlines (BBC uses <h2> tags for card headlines)
        headline_elements = soup.find_all("h2")

        headlines = []
        for element in headline_elements:
            text = element.get_text(strip=True)

            # Skip empty entries and ignore duplicate headlines
            if text and text not in headlines:
                headlines.append(text)

            # Stop collecting once we have 5 unique headlines
            if len(headlines) == 5:
                break

        # 5. Handle cases where fewer than 5 headlines are found
        if not headlines:
            print("No headlines found. Check the HTML selector.")
            return

        # 6. Print the headlines numbered 1 to 5
        for rank, title in enumerate(headlines, start=1):
            print(f"{rank}. {title}")

        if len(headlines) < 5:
            print(f"\nNote: Only {len(headlines)} headlines were available.")

    except requests.exceptions.RequestException as error:
        print(f"Network error occurred: {error}")


if __name__ == "__main__":
    fetch_top_headlines()