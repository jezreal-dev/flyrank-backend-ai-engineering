#!/usr/bin/env python3
"""
Raw one-shot AI-generated scraper (UNEDITED, saved for Bonus Stage B: "AI vs. Me").
Prompt: "Write a Python scraper that scrapes the first 3 pages of books.toscrape.com and saves the books to JSON."
"""

import json
import requests
from bs4 import BeautifulSoup

books = []

for page in range(1, 4):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for article in soup.select("article.product_pod"):
        title = article.select_one("h3 a").text
        link = "https://books.toscrape.com/catalogue/" + article.select_one("h3 a")["href"]
        price = article.select_one(".price_color").text
        availability = article.select_one(".availability").text.strip()
        rating = article.select_one("p.star-rating")["class"][1]

        books.append(
            {
                "title": title,
                "url": link,
                "price": price,
                "availability": availability,
                "rating": rating,
            }
        )

with open("books_ai.json", "w") as f:
    json.dump(books, f, indent=2)

print(f"Saved {len(books)} books to books_ai.json")
