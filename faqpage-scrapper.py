import os
import json
import csv
import datetime
import requests
import concurrent.futures
from lxml import html
from urllib.parse import urlparse

class FAQPageScraper:
    """
    A class to scrape web pages, detect JSON-LD FAQPage schema, and save relevant data.
    """
    def __init__(self, url_file, target_dir):
        self.url_file = url_file
        self.target_dir = target_dir
        self.html_dir = os.path.join(self.target_dir, "HTML")
        self.jsonld_dir = os.path.join(self.target_dir, "JSONLD")
        self.report_file = os.path.join(self.target_dir, f"report-{datetime.datetime.today().strftime('%m-%d-%Y')}.csv")
        self.urls = self.load_urls()
        self.setup_directories()
    
    def load_urls(self):
        """Loads URLs from the provided text file."""
        try:
            with open(self.url_file, 'r') as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        except Exception as e:
            print(f"Error loading URLs: {e}")
            return []
    
    def setup_directories(self):
        """Creates necessary directories if they don't exist."""
        os.makedirs(self.target_dir, exist_ok=True)
        os.makedirs(self.html_dir, exist_ok=True)
        os.makedirs(self.jsonld_dir, exist_ok=True)
    
    def fetch_page(self, url):
        """Fetches the web page content and checks for JSON-LD FAQPage schema."""
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            if response.status_code == 200:
                page_tree = html.fromstring(response.text)
                json_ld_data = self.extract_json_ld(response.text)
                faq_detected = any('@type' in data and data['@type'] == 'FAQPage' for data in json_ld_data)
                if faq_detected:
                    self.save_faq_data(url, response.text, json_ld_data)
                return [datetime.datetime.today().strftime('%-m/%-d/%Y'), url, status_code, 'Yes' if faq_detected else 'No']
            return [datetime.datetime.today().strftime('%-m/%-d/%Y'), url, status_code, 'No']
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return [datetime.datetime.today().strftime('%-m/%-d/%Y'), url, 'Error', 'No']
    
    def extract_json_ld(self, html_content):
        """Extracts JSON-LD data from the web page."""
        try:
            tree = html.fromstring(html_content)
            scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
            json_data = []
            for script in scripts:
                try:
                    json_data.append(json.loads(script))
                except json.JSONDecodeError:
                    continue
            return json_data
        except Exception as e:
            print(f"Error extracting JSON-LD: {e}")
            return []
    
    def save_faq_data(self, url, html_content, json_ld_data):
        """Saves FAQ-related HTML and JSON-LD data."""
        try:
            parsed_url = urlparse(url)
            filename = parsed_url.netloc.replace('.', '_') + parsed_url.path.replace('/', '_').strip('_')
            
            # Save HTML content
            tree = html.fromstring(html_content)
            faq_section = tree.xpath('//*[@id="main"]/div[3]')
            if faq_section:
                with open(os.path.join(self.html_dir, f"{filename}.html"), 'w', encoding='utf-8') as file:
                    file.write(html.tostring(faq_section[0], pretty_print=True).decode('utf-8'))
            
            # Save JSON-LD content
            with open(os.path.join(self.jsonld_dir, f"{filename}.json"), 'w', encoding='utf-8') as file:
                json.dump(json_ld_data, file, indent=4)
        except Exception as e:
            print(f"Error saving FAQ data for {url}: {e}")
    
    def generate_report(self, results):
        """Generates a CSV report with the collected data."""
        try:
            with open(self.report_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "URL", "Response-Code", "FAQ"])
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing report: {e}")
    
    def run(self):
        """Executes the scraping process in parallel."""
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.fetch_page, url): url for url in self.urls}
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        self.generate_report(results)
        print("Scraping complete. Report generated.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape URLs for FAQPage JSON-LD data.")
    parser.add_argument("url_file", help="Path to the text file containing URLs.")
    parser.add_argument("target_dir", help="Target directory for saving results.")
    args = parser.parse_args()
    scraper = FAQPageScraper(args.url_file, args.target_dir)
    scraper.run()
