import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

# if "ON_HEROKU" in os.environ:
if "RAILWAY_ENVIRONMENT" in os.environ:
    # Setup for Railway
    USER_NAME = os.environ.get("SECRET_KEY")
    PASSWORD = os.environ.get("DATABASE_URL")
else:
    # Load from local .env
    load_dotenv()
    USER_NAME = os.environ.get("USER_NAME")
    PASSWORD = os.environ.get("PASSWORD")

driver = webdriver.Chrome()

# Maximize Window
driver.maximize_window()
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

# Enter to the site
driver.get('https://www.linkedin.com/login')
time.sleep(2)

# Accept cookies
driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/section/div/div[2]/button[2]").click()

# User Credentials
driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(USER_NAME)
driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(PASSWORD)
time.sleep(1)

# Login button
driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button').click()
driver.implicitly_wait(30)

# Jobs page
driver.get("https://www.linkedin.com/jobs/?")
time.sleep(3)
# Go to search results directly
driver.get("https://www.linkedin.com/jobs/search/?currentJobId=3477736514&geoId=105072130&keywords=python%20web%20developer&location=Poland&refresh=true")
time.sleep(1)

# Get all links for these offers
links = []
# Navigate 1 pages
print('Links are being collected now.')
try:
    for page in range(2, 3):
        time.sleep(2)
        jobs_block = driver.find_element(By.CLASS_NAME,'scaffold-layout__list-container')
        jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')
        print(f'page: {page}\njobs_block: {jobs_block}\njobs_list: {jobs_list} ')

        for job in jobs_list:
            all_links = job.find_elements(By.TAG_NAME,'a')
            for a in all_links:
                if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute(
                        'href') not in links:
                    links.append(a.get_attribute('href'))
                    print(a.get_attribute('href'))
                else:
                    pass
            # scroll down for each job element
            driver.execute_script("arguments[0].scrollIntoView();", job)

        print(f'Collecting the links in the page: {page - 1}')
        # go to next page:
        driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()
        time.sleep(3)
except:
    pass
print('Found ' + str(len(links)) + ' links for job offers')

# Create empty lists to store information
job_titles = []
company_names = []
company_locations = []
work_methods = []
post_dates = []
work_times = []
job_desc = []

i = 0
j = 1
# Visit each link one by one to scrape the information
print('Visiting the links and collecting information just started.')
# for i in range(len(links)):
for i in range(2):
    try:
        driver.get(links[i])
        i += 1
        time.sleep(2)
        # Click See more.
        driver.find_element(By.ID, "ember33").click()
        time.sleep(2)
    except:
        pass

    # Find the general information of the job offers
    contents = driver.find_elements(By.CLASS_NAME,'p5')
    for content in contents:
        try:
            job_titles.append(content.find_element(By.TAG_NAME,"h1").text)
            company_names.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__company-name").text)
            company_locations.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__bullet").text)
            work_methods.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__workplace-type").text)
            post_dates.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__posted-date").text)
            work_times.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__job-insight").text)
            print(f'Scraping the Job Offer {j} DONE.')
            print(f'job_titles: {content.find_element(By.TAG_NAME,"h1").text}\n, '
                  f'company_names: {content.find_element(By.CLASS_NAME,"jobs-unified-top-card__company-name").text}\n, '
                  f'company_locations: {content.find_element(By.CLASS_NAME,"jobs-unified-top-card__bullet").text}\n, '
                  f'work_methods: {content.find_element(By.CLASS_NAME,"jobs-unified-top-card__workplace-type").text}\n, '
                  f'post_dates: {content.find_element(By.CLASS_NAME,"jobs-unified-top-card__posted-date").text}\n, '
                  f'work_times: {content.find_element(By.CLASS_NAME,"jobs-unified-top-card__job-insight").text}\n, '
                  )
            j += 1

        except:
            pass
        time.sleep(2)

    # Scraping the job description
    job_description = driver.find_elements(By.CLASS_NAME,'jobs-description__content')
    for description in job_description:
        job_text = description.find_element(By.CLASS_NAME,"jobs-box__html-content").text
        job_desc.append(job_text)
        print(f'Scraping the Job Offer {j}')
        print(job_text)
        time.sleep(2)

    # Creating the dataframe
df = pd.DataFrame(list(zip(job_titles, company_names,
                           company_locations, work_methods,
                           post_dates, work_times, job_desc)),
                  columns=['job_title', 'company_name',
                           'company_location', 'work_method',
                           'post_date', 'work_time', 'job_desc'])

# Storing the data to csv file
df.to_csv('job_offers.csv', index=False)