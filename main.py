import logging
import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

class LinkedInJobsScraper:
    LOGIN_URL = 'https://www.linkedin.com/login'
    JOB_SEARCH_URL = 'https://www.linkedin.com/jobs/search/?currentJobId=3477736514&geoId=105072130&keywords=python%20web%20developer&location=Poland&refresh=true'

    LOGIN_USERNAME_XPATH = '//input[@id="username"]'
    LOGIN_PASSWORD_XPATH = '//input[@id="password"]'
    LOGIN_BUTTON_XPATH = '//button[contains(text(),"Sign in")]'

    JOB_LIST_BLOCK_CLASSNAME = 'scaffold-layout__list-container'
    JOB_LIST_ITEM_CSS_SELECTOR = '.jobs-search-results__list-item'
    JOB_HEADER_CLASSNAME = 'jobs-unified-top-card__content--two-pane'
    JOB_DESCRIPTION_CLASSNAME = 'jobs-box__html-content'
    JOB_LINK_TAGNAME = 'a'
    JOB_TITLE_CLASSNAME = 'jobs-unified-top-card__job-title'
    COMPANY_NAME_CLASSNAME = 'jobs-unified-top-card__company-name'
    LOCATION_CLASSNAME = 'jobs-unified-top-card__bullet'
    JOB_TYPE_CLASSNAME = 'jobs-unified-top-card__workplace-type'
    POST_DATE_CLASSNAME = 'jobs-unified-top-card__posted-date'
    APPLICANT_COUNT_CLASSNAME = 'jobs-unified-top-card__applicant-count'
    SKILLS_LIST_CLASSNAME = 'job-details-skill-match-status-list__unmatched-skill'
    SKILLS_ITEM_CSS_SELECTOR = '.job-details-skill-match-status-list__unmatched-skill div[aria-label]'

    # SHOW_MORE_DESCR_BUTTON_XPATH = '//*[@id="ember33"]'
    SHOW_MORE_SKILLS_BUTTON_XPATH = '//*[@id="main"]/div/section[2]/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/div[2]/ul/div/button'
    CLOSE_BUTTON_SKILLS_ID = '.artdeco-modal__dismiss'

    LAST_PAGE = 3

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
        self.jobs_list = []
        self.job_link = None
        self.main_window_id = None
        self.skills_window_id = None

    def login(self):
        self.driver.maximize_window()
        self.driver.get(self.LOGIN_URL)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_USERNAME_XPATH))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_PASSWORD_XPATH))).send_keys(self.password)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, self.LOGIN_BUTTON_XPATH))).click()
        self.wait.until(EC.url_changes(self.LOGIN_URL))

    def scrape_job_item_details(self, each_job) -> {}:
        job_item_data = {}
        try:
            self.job_link = each_job.find_element(By.TAG_NAME, self.JOB_LINK_TAGNAME)
            if self.job_link and str(self.job_link.get_attribute("href")).startswith("https://www.linkedin.com/jobs/view"):
                logging.info(f'Scraped information for job link:\n{self.job_link.get_attribute("href")}')
            else:
                logging.info(f'Failed to scrap information for job link')
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            job_header_locator = (By.CLASS_NAME, self.JOB_HEADER_CLASSNAME)
            self.wait.until(EC.presence_of_element_located(job_header_locator))

            job_description_header = soup.find('div', {'class': self.JOB_HEADER_CLASSNAME})

            # Job Title
            job_title_elem = job_description_header.find('h2', {'class': self.JOB_TITLE_CLASSNAME})
            if job_title_elem:
                job_item_data['Job Title'] = job_title_elem.text.strip()
                logging.info(f"Scraped information for Job Title: {job_item_data['Job Title']}")
            else:
                job_item_data['Job Title'] = 'Error while scraping'
                logging.warning('Job title not found.')

            # Company Name
            company_name_elem = job_description_header.find('span', {'class': self.COMPANY_NAME_CLASSNAME})
            if company_name_elem:
                job_item_data['Company Name'] = company_name_elem.text.strip()
                logging.info(f"Scraped information for Company Name: {job_item_data['Company Name']}")
            else:
                job_item_data['Company Name'] = 'Error while scraping'
                logging.warning('Company name not found.')

            # Location
            location_elem = job_description_header.find('span', {'class': self.LOCATION_CLASSNAME})
            if location_elem:
                job_item_data['Location'] = location_elem.text.strip()
                logging.info(f"Scraped information for Location: {job_item_data['Location']}")
            else:
                job_item_data['Location'] = 'Error while scraping'
                logging.warning('Location not found.')

            # Job Type
            job_type_elem = job_description_header.find('span', {'class': self.JOB_TYPE_CLASSNAME})
            if job_type_elem:
                job_item_data['Job Type'] = job_type_elem.text.strip()
                logging.info(f"Scraped information for Job Type: {job_item_data['Job Type']}")
            else:
                job_item_data['Job Type'] = 'Error while scraping'
                logging.warning('Job type not found.')

            # Post Aging
            post_date_elem = job_description_header.find('span', {'class': self.POST_DATE_CLASSNAME})
            if post_date_elem:
                job_item_data['Post Aging'] = post_date_elem.text.strip()
                logging.info(f"Scraped information for Post Aging: {job_item_data['Post Aging']}")
            else:
                job_item_data['Post Aging'] = 'Error while scraping'
                logging.warning('Post Aging not found.')

            # Applicant Count
            applicant_count_elem = job_description_header.find('span',
                                                               {'class': self.APPLICANT_COUNT_CLASSNAME})
            if applicant_count_elem is not None:
                applicant_count_text = applicant_count_elem.text.strip()
                try:
                    job_item_data['Applicant Count'] = int(applicant_count_text.split()[0])
                    logging.info(f"Scraped information for Applicant Count: {job_item_data['Applicant Count']} applicants")
                except ValueError:
                    logging.warning(f"Could not parse applicant count from text: {applicant_count_text}")
                    job_item_data['Applicant Count'] = 'Error while scraping'
            else:
                job_item_data['Applicant Count'] = 'Error while scraping'
                logging.warning('Applicant count not found.')

            # Skills Required
            try:
                show_more_skills_button = self.driver.find_element(By.XPATH, self.SHOW_MORE_SKILLS_BUTTON_XPATH)
                self.driver.execute_script("arguments[0].scrollIntoView();", show_more_skills_button)
                show_more_skills_button.click()
                skills_window_locator = (By.CLASS_NAME, self.SKILLS_LIST_CLASSNAME)
                self.wait.until(EC.presence_of_element_located(skills_window_locator))
                self.skills_window_id = self.driver.current_window_handle
                if self.skills_window_id is not None:
                    print(f'skills_window_id assigned: {self.skills_window_id}')
                try:
                    html_skills = self.driver.page_source
                    if html_skills:
                        html_skills_parsed = BeautifulSoup(html_skills, 'html.parser')
                        skill_list = html_skills_parsed.select('.job-details-skill-match-status-list__unmatched-skill div[aria-label]')
                        skills_str_text = ', '.join(skill.text.strip() for skill in skill_list)
                        if skills_str_text:
                            job_item_data['Skills Required'] = skills_str_text
                            logging.info(f"Scraped information for Skills Required: {job_item_data['Skills Required']}")
                        else:
                            job_item_data['Skills Required'] = 'Error while scraping'
                            logging.warning('Skills Required not found.')
                    else:
                        job_item_data['Skills Required'] = 'Error while scraping'
                        logging.warning('Skills Required not found.')
                finally:
                    all_windows = self.driver.window_handles
                    for each_window in all_windows:
                        if each_window != self.main_window_id:
                            self.driver.switch_to.window(each_window)
                            self.driver.close()
            except TimeoutException as e:
                logging.error(
                    f'Error: Timeout occurred while waiting for skills to load on page: {e}\nfor {self.job_link.get_attribute("href")}')
                job_item_data['Skills Required'] = 'Error while scraping'

            # Job Description
            job_description_elem = soup.find('div', {'class': self.JOB_DESCRIPTION_CLASSNAME})
            if job_description_elem:
                job_item_data['Job Description'] = job_description_elem.text.strip()
                logging.info(f"Scraped information for Job Description: {str(job_item_data['Job Description'])[300]}")
            else:
                job_item_data['Job Description'] = 'Error while scraping'
                logging.info('Job description not found.')

            # Job Link
            if self.job_link and str(self.job_link.get_attribute("href")).startswith("https://www.linkedin.com/jobs/view"):
                job_item_data['Job Link'] = self.job_link.get_attribute("href")
                logging.info(f"Job Link saved")
            else:
                job_item_data['Job Link'] = 'Error while scraping'
                logging.info(f"Job Link failed to be saved")

        except TimeoutException as e:
            logging.error(f'Error: Timeout occurred while waiting for an element to load on page: {e}\nfor {self.job_link.get_attribute("href")}')
        except NoSuchElementException as e:
            logging.error(f'Error: Element not found while scraping job information: {e}\nfor {self.job_link.get_attribute("href")}')
        except Exception as e:
            logging.error(f'Error occurred while scraping job information: {e}\nfor {self.job_link.get_attribute("href")}')
        finally:
            logging.info(f'Scraping a Job Offer DONE.')
        return job_item_data

    def scrape_jobs_info(self) -> []:
        job_data_list_of_dict = []
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ember13"]'))).click()  # Accept cookies
            logging.info(f"Cookies accepted.")
        except NoSuchElementException as e:
            logging.info(f"Cookies button not found.")
        for page in range(2, self.LAST_PAGE):
            self.main_window_id = self.driver.current_window_handle
            logging.info(f"Collecting job offer info just started on the page {page - 1}")
            self.jobs_list = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.JOB_LIST_ITEM_CSS_SELECTOR)))
            if self.jobs_list:
                logging.info(f"Scraped Job List objects.")
                for i, each_job in enumerate(self.jobs_list[:1]):
                    each_job.click()
                    job_data = self.scrape_job_item_details(each_job)
                    job_data_list_of_dict.append(job_data)
                    # Re-fetch the job list items to ensure they are up-to-date with the current state of the page
                    self.jobs_list = self.wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.JOB_LIST_ITEM_CSS_SELECTOR)))
            else:
                logging.warning('Job List not found.')
            # if page != self.LAST_PAGE:
                #  self.driver.find_element(By.CSS_SELECTOR, f'button[aria-label="Page {page}"]').click()

                # element = self.wait.until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, f'button[aria-label="Page {page}"]')))
                # actions = ActionChains(self.driver)
                # actions.move_to_element(element).perform()
                # element.click()

                # page_2_button = self.wait.until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Page 2"]')))
                # # Use the wait object to wait for the element to be clickable
                # page_2_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Page 2"]')))
                # # Click the button
                # page_2_button.click()

        return job_data_list_of_dict

    def scrape_jobs(self):
        try:
            self.login()
            self.driver.get(self.JOB_SEARCH_URL)
            job_data_list_of_dict = self.scrape_jobs_info()
            df = pd.DataFrame(job_data_list_of_dict)
            print(df)
            df.to_csv('job_offers.csv', index=False)
            logging.info(f'Saved data for {len(job_data_list_of_dict)} job offers')
        except Exception as e:
            logging.error(f'Error occurred while scraping jobs: {e}')
        finally:
            self.driver.quit()




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    scraper = LinkedInJobsScraper()
    scraper.scrape_jobs()
