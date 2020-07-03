from DataScraper import DataScraper


def main():
    scraper = DataScraper(queue_size=5)
    scraper.run_scraper()


if __name__ == "__main__":
    main()
