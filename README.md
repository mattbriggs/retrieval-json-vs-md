# FAQ Page Scraper

## Overview

This script scrapes a list of URLs, detects JSON-LD FAQPage schema, and extracts relevant data. It also saves FAQ-related HTML and JSON-LD data when detected.

## Features

- Fetches web pages in parallel for efficiency.
- Detects `FAQPage` in JSON-LD schema.
- Saves extracted FAQ section HTML and JSON-LD if found.
- Generates a CSV report with scraping results.
- Handles errors and timeouts gracefully.

## Requirements

- Python 3.8+
- Required dependencies (install using `pip install -r requirements.txt`)

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```bash
python faqpage-scrapper.py <url_file> <target_dir>
```

Parameters
- <url_file>: Path to a text file containing URLs.
- <target_dir>: Directory to save reports and extracted files.

### Output
- report-<date>.csv: CSV file containing URL response data.
- HTML/: Folder with extracted FAQ HTML sections.
- JSONLD/: Folder with extracted JSON-LD schema data.

### Example

```bash
python faq_scraper.py urls.txt output/
```

### Notes
 - Ensure the URLs file is correctly formatted with one URL per line.
 - The script uses multi-threading to process URLs in parallel.
 - JSON-LD is validated before saving.

## License

MIT License