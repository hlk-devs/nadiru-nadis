# nadi-scraper

Generate runnable web scraping scripts with Nadiru.

## Requirements

- Python 3.11+
- `httpx` (`pip install httpx`)
- Running Nadiru engine at `http://localhost:8765`

## Usage

```bash
python scraper.py "scrape product names and prices from example.com/shop"
python scraper.py "get all article headlines from news.example.com" --output json
python scraper.py "download all images from example.com/gallery" --output script
```

## Output modes

- `--output json` (default): asks for a script oriented around JSON output.
- `--output script`: saves generated script to `generated_scraper.py`.

The request uses `priority: "quality"` and prints routing details at the end.
