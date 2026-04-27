# nadi-scraper

**Describe what you want to scrape in plain English, get back a runnable Python scraper.**

A code-generation Nadi. You give it a description like "scrape product names and prices from example.com/shop" and it returns a working scraper script. Behind the scenes it uses `priority: "quality"` because writing parser code that actually works on real HTML is harder than it looks, and cheap models tend to produce scrapers that break on the first edge case.

## Usage
