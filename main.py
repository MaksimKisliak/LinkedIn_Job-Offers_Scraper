import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os


class LinkedInJobsScraper:
    LOGIN_URL = 'https://www.linkedin.com/login'
    JOB_SEARCH_URL = 'https://www.linkedin.com/jobs/search/?currentJobId=3477736514&geoId=105072130&keywords=python%20web%20developer&location=Poland&refresh=true'

    LOGIN_USERNAME_XPATH = '//input[@id="username"]'
    LOGIN_PASSWORD_XPATH = '//input[@id="password"]'
    LOGIN_BUTTON_XPATH = '//button[contains(text(),"Sign in")]'

    JOB_LIST_BLOCK_CLASSNAME = 'scaffold-layout__list-container'
    JOB_LIST_ITEM_CLASSNAME = '.jobs-search-results__list-item'
    JOB_ITEM_CLASSNAME = 'p5'
    JOB_LINK_TAGNAME = 'a'
    JOB_TITLE_TAGNAME = 'h1'
    COMPANY_NAME_CLASSNAME = 'jobs-unified-top-card__company-name'
    LOCATION_CLASSNAME = 'jobs-unified-top-card__bullet'
    JOB_TYPE_CLASSNAME = 'jobs-unified-top-card__workplace-type'
    POST_DATE_CLASSNAME = 'jobs-unified-top-card__posted-date'
    JOB_DESC_CLASSNAME = 'jobs-box__html-content'
    SHOW_MORE_BUTTON_XPATH = '//*[@id="ember33"]'

    def __init__(self):
        if "RAILWAY_ENVIRONMENT" in os.environ:
            # Setup for Railway
            user_name = os.environ.get("USER_NAME")
            password = os.environ.get("PASSWORD")
        else:
            # Load from local .env
            load_dotenv()
            user_name = os.environ.get("USER_NAME")
            password = os.environ.get("PASSWORD")

        self.username = user_name
        self.password = password
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        self.driver.maximize_window()
        self.driver.get(self.LOGIN_URL)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_USERNAME_XPATH))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_PASSWORD_XPATH))).send_keys(self.password)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, self.LOGIN_BUTTON_XPATH))).click()
        self.wait.until(EC.url_changes(self.LOGIN_URL))

    def scrape_job_links(self):
        job_links = []
        for page in range(2, 3):
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ember13"]'))).click()  # Accept cookies
                logging.info(f"Collecting job offer links just started on the page {page-1}")
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, self.JOB_LIST_BLOCK_CLASSNAME)))
                jobs_block = self.driver.find_element(By.CLASS_NAME, self.JOB_LIST_BLOCK_CLASSNAME)
                logging.info(f"Scraped information for jobs_block: {jobs_block}")
                jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, self.JOB_LIST_ITEM_CLASSNAME)
                logging.info(f"Scraped information for jobs_list: {jobs_list}")
                for each_job in jobs_list[:3]:
                    each_job_links = each_job.find_elements(By.TAG_NAME, self.JOB_LINK_TAGNAME)
                    logging.info(f"Scraped information for {jobs_list}")
                    for each_job_link in each_job_links:
                        if str(each_job_link.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and each_job_link.get_attribute('href') not in job_links:
                            job_links.append(each_job_link.get_attribute("href"))
                    self.driver.execute_script("arguments[0].scrollIntoView();", each_job)
            except Exception as e:
                logging.error(f'Error occurred while scraping job links: {e}')
            self.driver.find_element(By.CSS_SELECTOR, f'button[aria-label="Page {page}"]').click()
        logging.info(f'Found {len(job_links)} job offer links')
        return job_links

    def scrape_job_info(self, job_link):
        job_data = {}
        try:
            logging.info(f"Visiting the link and collecting information just started.")
            self.driver.get(job_link)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, self.SHOW_MORE_BUTTON_XPATH))).click()  # Show More
            logging.info(f"Cookies accepted.")
            logging.info(f"Finding the general information of a job offer: {job_link}.")
            job_description = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, self.JOB_ITEM_CLASSNAME)))

            job_data['Job Title'] = job_description.find_element(By.TAG_NAME, self.JOB_TITLE_TAGNAME).text
            logging.info(f"Scraped information for {job_data['Job Title']}")

            job_data['Company Name'] = job_description.find_element(By.CLASS_NAME, self.COMPANY_NAME_CLASSNAME).text
            logging.info(f"Scraped information for {job_data['Company Name']}")

            job_data['Location'] = job_description.find_element(By.CLASS_NAME, self.LOCATION_CLASSNAME).text
            logging.info(f"Scraped information for {job_data['Location']}")

            job_data['Job Type'] = job_description.find_element(By.CLASS_NAME, self.JOB_TYPE_CLASSNAME).text
            logging.info(f"Scraped information for {job_data['Job Type']}")

            job_data['Post Date'] = job_description.find_element(By.CLASS_NAME, self.POST_DATE_CLASSNAME).text
            logging.info(f"Scraped information for {job_data['Post Date']}")

            job_data['Job Description'] = job_description.find_element(By.CLASS_NAME, self.JOB_DESC_CLASSNAME).text
            logging.info(f"Scraped information for {job_data['Job Description']}")

        except Exception as e:
            logging.error(f'Error occurred while scraping job information for {job_link}: {e}')
        else:
            logging.info(f"Scraping the Job Offer {job_data} DONE.")
            return job_data

    def scrape_jobs(self):
        try:
            self.login()
            self.driver.get(self.JOB_SEARCH_URL)
            job_links = self.scrape_job_links()
            print(job_links)
            job_data = [self.scrape_job_info(job_link) for job_link in job_links]
            print(job_data)
            df = pd.DataFrame(job_data)
            df.to_csv('job_offers.csv', index=False)
            logging.info(f'Saved data for {len(job_data)} job offers')
        except Exception as e:
            logging.error(f'Error occurred while scraping jobs: {e}')
        finally:
            self.driver.quit()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    scraper = LinkedInJobsScraper()
    scraper.scrape_jobs()

