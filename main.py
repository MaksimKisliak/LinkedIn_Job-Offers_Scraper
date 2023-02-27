import logging
import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


class LinkedInJobsScraper:
    LOGIN_URL = 'https://www.linkedin.com/login'
    JOB_SEARCH_URL = \
    'https://www.linkedin.com/jobs/search/?currentJobId=3477736514&geoId=105072130&keywords=python%20web%20developer&location=Poland&refresh=true'

    LOGIN_USERNAME_XPATH = '//input[@id="username"]'
    LOGIN_PASSWORD_XPATH = '//input[@id="password"]'

    JOB_LIST_CONTAINER_CLASSNAME = 'scaffold-layout__list-container'
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

    LOGIN_BUTTON_XPATH = '//button[contains(text(),"Sign in")]'
    SHOW_MORE_SKILLS_BUTTON_XPATH = '//*[@id="main"]/div/section[2]/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/div[2]/ul/div/button'
    CLOSE_BUTTON_SKILLS_CSS_SELECTOR = "button[data-test-modal-close-btn]"

    LAST_PAGE = 3

    # Initialize class variables and set up the Selenium driver
    def __init__(self):
        if "RAILWAY_ENVIRONMENT" in os.environ:
            # Check if the script is running on the Railway platform
            user_name = os.environ.get("USER_NAME")
            password = os.environ.get("PASSWORD")
        else:
            # Load from local .env
            load_dotenv()
            user_name = os.environ.get("USER_NAME")
            password = os.environ.get("PASSWORD")

        # Store credentials and create Selenium driver
        self.username = user_name
        self.password = password
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.jobs_list = []
        self.job_item_data = {}
        self.job_link = None

    # Log in to LinkedIn
    def login(self):
        self.driver.maximize_window()
        self.driver.get(self.LOGIN_URL)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_USERNAME_XPATH))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.LOGIN_PASSWORD_XPATH))).send_keys(self.password)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, self.LOGIN_BUTTON_XPATH))).click()
        self.wait.until(EC.url_changes(self.LOGIN_URL))

    def scrape_job_item_details(self):
        # Accept cookies
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-global-alert__action"))).click()
            logging.info(f"Cookies accepted.")
        except Exception as e:
            logging.info(f"Cookies button not found. {e}")
        job_data_list_of_dict_all_pages = []

        # Collect job offer information from multiple pages
        for page in range(2, self.LAST_PAGE):
            logging.info(f"Collecting job offer info just started on the page {page - 1}.")
            jobs_block = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, self.JOB_LIST_CONTAINER_CLASSNAME)))
            self.jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, self.JOB_LIST_ITEM_CSS_SELECTOR)
            if self.jobs_list:
                logging.info(f"Scraped Job List objects on the page {page - 1}.")
                for each_job in self.jobs_list:
                    self.job_item_data = {}
                    each_job.click()
                    try:

                        # Scrapping Job Link
                        self.job_link = each_job.find_element(By.TAG_NAME, self.JOB_LINK_TAGNAME)
                        if self.job_link and str(self.job_link.get_attribute("href")).startswith(
                                "https://www.linkedin.com/jobs/view"):
                            logging.info(f'Scraped information for job link:\n{self.job_link.get_attribute("href")}')
                        else:
                            logging.info(f'Failed to scrap information for job link')

                        # Parsing the current html page
                        html = self.driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')

                        job_header_locator = (By.CLASS_NAME, self.JOB_HEADER_CLASSNAME)
                        self.wait.until(EC.presence_of_element_located(job_header_locator))

                        job_description_header = soup.find('div', {'class': self.JOB_HEADER_CLASSNAME})

                        # Job Title
                        job_title_elem = job_description_header.find('h2', {'class': self.JOB_TITLE_CLASSNAME})
                        if job_title_elem:
                            self.job_item_data['Job Title'] = job_title_elem.text.strip()
                            logging.info(f"Scraped information for Job Title: {self.job_item_data['Job Title']}")
                        else:
                            self.job_item_data['Job Title'] = 'Null'
                            logging.warning('Job title not found.')

                        # Company Name
                        company_name_elem = job_description_header.find('span', {'class': self.COMPANY_NAME_CLASSNAME})
                        if company_name_elem:
                            self.job_item_data['Company Name'] = company_name_elem.text.strip()
                            logging.info(f"Scraped information for Company Name: {self.job_item_data['Company Name']}")
                        else:
                            self.job_item_data['Company Name'] = 'Null'
                            logging.warning('Company name not found.')

                        # Location
                        location_elem = job_description_header.find('span', {'class': self.LOCATION_CLASSNAME})
                        if location_elem:
                            self.job_item_data['Location'] = location_elem.text.strip()
                            logging.info(f"Scraped information for Location: {self.job_item_data['Location']}")
                        else:
                            self.job_item_data['Location'] = 'Null'
                            logging.warning('Location not found.')

                        # Job Type
                        job_type_elem = job_description_header.find('span', {'class': self.JOB_TYPE_CLASSNAME})
                        if job_type_elem:
                            self.job_item_data['Job Type'] = job_type_elem.text.strip()
                            logging.info(f"Scraped information for Job Type: {self.job_item_data['Job Type']}")
                        else:
                            self.job_item_data['Job Type'] = 'Null'
                            logging.warning('Job type not found.')

                        # Post Aging
                        post_date_elem = job_description_header.find('span', {'class': self.POST_DATE_CLASSNAME})
                        if post_date_elem:
                            self.job_item_data['Post Aging'] = post_date_elem.text.strip()
                            logging.info(f"Scraped information for Post Aging: {self.job_item_data['Post Aging']}")
                        else:
                            self.job_item_data['Post Aging'] = 'Null'
                            logging.warning('Post Aging not found.')

                        # Applicant Count
                        applicant_count_elem = job_description_header.find('span',
                                                                           {'class': self.APPLICANT_COUNT_CLASSNAME})
                        if applicant_count_elem is not None:
                            applicant_count_text = applicant_count_elem.text.strip()
                            try:
                                self.job_item_data['Applicant Count'] = int(applicant_count_text.split()[0])
                                logging.info(
                                    f"Scraped information for Applicant Count:"
                                    f" {self.job_item_data['Applicant Count']} applicants")
                            except ValueError:
                                logging.warning(f"Could not parse applicant count from text: {applicant_count_text}")
                                self.job_item_data['Applicant Count'] = 'Null'
                        else:
                            self.job_item_data['Applicant Count'] = 'Null'
                            logging.warning('Applicant count not found.')

                        # Skills Required
                        try:
                            show_more_skills_button_locator = (By.XPATH, self.SHOW_MORE_SKILLS_BUTTON_XPATH)
                            self.wait.until(EC.presence_of_element_located(show_more_skills_button_locator))
                            show_more_skills_button = self.driver.find_element(By.XPATH, self.SHOW_MORE_SKILLS_BUTTON_XPATH)
                            self.driver.execute_script("arguments[0].scrollIntoView();", show_more_skills_button)
                            show_more_skills_button.click()
                            skills_window_locator = (By.CLASS_NAME, self.SKILLS_LIST_CLASSNAME)
                            self.wait.until(EC.presence_of_element_located(skills_window_locator))
                            try:
                                html_skills = self.driver.page_source
                                if html_skills:
                                    html_skills_parsed = BeautifulSoup(html_skills, 'html.parser')
                                    skill_list = html_skills_parsed.select(
                                        '.job-details-skill-match-status-list__unmatched-skill div[aria-label]')
                                    skills_str_text = ', '.join(skill.text.strip() for skill in skill_list)
                                    if skills_str_text:
                                        self.job_item_data['Skills Required'] = skills_str_text
                                        logging.info(
                                            f"Scraped information for Skills Required:"
                                            f" {self.job_item_data['Skills Required']}")
                                    else:
                                        self.job_item_data['Skills Required'] = 'Null'
                                        logging.warning('Skills Required not found.')
                                else:
                                    self.job_item_data['Skills Required'] = 'Null'
                                    logging.warning('Skills Required not found.')
                            finally:
                                close_button = self.wait.until(EC.visibility_of_element_located(
                                    (By.CSS_SELECTOR, self.CLOSE_BUTTON_SKILLS_CSS_SELECTOR)))
                                close_button.click()
                                logging.info('Skills window closed')
                        except TimeoutException as e:
                            logging.error(
                                f'Error: Timeout occurred while waiting for skills to load on page:'
                                f' {e}\nfor {self.job_link.get_attribute("href")}')
                            self.job_item_data['Skills Required'] = 'Null'
                        except NoSuchElementException as e:
                            logging.error(
                                f'Error: Element not found while scraping show_more_skills_button: {e}')
                        except Exception as e:
                            logging.error(
                                f'Error: Element not found while scraping show_more_skills_button: {e}')

                        # Job Description
                        job_description_elem = soup.find('div', {'class': self.JOB_DESCRIPTION_CLASSNAME})
                        if job_description_elem:
                            self.job_item_data['Job Description'] = job_description_elem.text.strip()
                            logging.info(
                                f"Scraped information for Job Description: "
                                f"{(str(self.job_item_data['Job Description']))[:300]}")
                        else:
                            self.job_item_data['Job Description'] = 'Null'
                            logging.info('Job description not found.')

                        # Job Link
                        if self.job_link and str(self.job_link.get_attribute("href")).startswith(
                                "https://www.linkedin.com/jobs/view"):
                            self.job_item_data['Job Link'] = self.job_link.get_attribute("href")
                            logging.info(f"Job Link saved")
                        else:
                            self.job_item_data['Job Link'] = 'Null'
                            logging.info(f"Job Link failed to be saved")

                        # Add a new dict to the list (a new row for the pandas df)
                        job_data_list_of_dict_all_pages.append(self.job_item_data)

                        self.driver.execute_script("arguments[0].scrollIntoView();", each_job)

                    except TimeoutException as e:
                        logging.error(
                            f'Error: Timeout occurred while waiting for an element to load on page:'
                            f' {e}\nfor {self.job_link.get_attribute("href")}')
                    except NoSuchElementException as e:
                        logging.error(
                            f'Error: Element not found while scraping job information:'
                            f' {e}\nfor {self.job_link.get_attribute("href")}')
                    except Exception as e:
                        logging.error(
                            f'Error occurred while scraping job information:'
                            f' {e}\nfor {self.job_link.get_attribute("href")}')
                    finally:
                        logging.info(f'Scraping a Job Offer DONE.')
            else:
                logging.warning('Job List not found.')

            #  Click the next page functionality
            try:
                self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()  # dynamic path
                # next_page_button_locator = (By.XPATH, f"//button[@aria-label='Page {page}']")  # dynamic path
                # self.wait.until(EC.presence_of_element_located(next_page_button_locator))
                # next_page_button = self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']")
                # next_page_button.click()
            except Exception as e:
                logging.error(f'Failed to proceed to the next page: {page}: {e}')

        return job_data_list_of_dict_all_pages

    def scrape_jobs(self):
        try:
            # Login to LinkedIn
            self.login()
            # Navigate to job search page
            self.driver.get(self.JOB_SEARCH_URL)
            # Scrape job details
            job_data_list_of_dict_for_df = self.scrape_job_item_details()
            # Create pandas dataframe from job data and save to csv file
            df = pd.DataFrame(job_data_list_of_dict_for_df)
            print(df)
            df.to_csv('job_offers.csv', index=False)
            logging.info(f'Saved data for {len(job_data_list_of_dict_for_df)} job offers')
        except Exception as e:
            logging.error(f'Error occurred while scraping jobs: {e}')
        finally:
            # Close the driver and end the session
            self.driver.quit()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    scraper = LinkedInJobsScraper()
    scraper.scrape_jobs()
