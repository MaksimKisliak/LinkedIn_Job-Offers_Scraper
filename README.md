# LinkedIn Job Postings Web Scraper
<p>This is a Python script for web scraping LinkedIn job postings. The script uses Selenium and Beautiful Soup libraries to automate browser actions and parse HTML, respectively.</p>Prerequisites
<ul>
 <li>Python 3.x</li>
 <li><code>pip</code> package installer</li>
 <li>Chrome web browser</li>
 <li>ChromeDriver (matching the Chrome version installed)</li></ul>





## Usage
<p>To run the script, execute <code>python linkedin_job_scraper.py</code> in the terminal. The script will log in to LinkedIn, navigate to the job search URL, scrape the job postings, and save the data to a CSV file named <code>job_offers.csv</code>.
<p>The LinkedInJobsScraper class provides two main methods:</p>
<ul>
 <li><p><code>scrape_jobs</code>: This method logs in to LinkedIn, navigates to the job search page, and scrapes job offer details from multiple pages of search results. The data is saved to a CSV file named 'job_offers.csv'.</p></li>
 <li><p><code>scrape_job_item_details</code>: This method scrapes the job details from a single job offer page. This is called by <code>scrape_jobs</code> method and can be used to scrape job details for a specific job offer.</p></li></ul>

 ## Configuration
<ol>
 <li>Set environment variables <code>USER_NAME</code> and <code>PASSWORD</code> with your LinkedIn credentials.</li>
 <li>Update the following constants in the <code>LinkedInJobsScraper</code> class:</li>
</ol>
 <li><code>JOB_SEARCH_URL</code>: the URL for the job search page.</li>
 <li><code>LOGIN_URL</code>: the URL for the LinkedIn login page.</li>
 <li><code>LOGIN_USERNAME_XPATH</code>: the XPATH for the username field on the login page.</li>
 <li><code>LOGIN_PASSWORD_XPATH</code>: the XPATH for the password field on the login page.</li>
 <li><code>LOGIN_BUTTON_XPATH</code>: the XPATH for the login button on the login page.</li>
 <li><code>JOB_LIST_CONTAINER_CLASSNAME</code>: the CSS class name for the container element that holds the job offer list on the job search page.</li>
 <li><code>JOB_LIST_ITEM_CSS_SELECTOR</code>: the CSS selector for each job offer element in the job offer list.</li>
 <li><code>JOB_HEADER_CLASSNAME</code>: the CSS class name for the job offer header element on a job offer page.</li>
 <li><code>JOB_TITLE_CLASSNAME</code>: the CSS class name for the job title element in the job offer header.</li>
 <li><code>COMPANY_NAME_CLASSNAME</code>: the CSS class name for the company name element in the job offer header.</li>
 <li><code>LOCATION_CLASSNAME</code>: the CSS class name for the location element in the job offer header.</li>
 <li><code>JOB_TYPE_CLASSNAME</code>: the CSS class name for the job type element in the job offer header.</li>
 <li><code>POST_DATE_CLASSNAME</code>: the CSS class name for the post date element in the job offer header.</li>
 <li><code>APPLICANT_COUNT_CLASSNAME</code>: the CSS class name for the applicant count element in the job offer header.</li>
 <li><code>JOB_DESCRIPTION_CLASSNAME</code>: the CSS class name for the job description element on a job offer page.</li>
 <li><code>JOB_LINK_TAGNAME</code>: the HTML tag name for the job offer link in the job offer list.</li>
 <li><code>SHOW_MORE_SKILLS_BUTTON_XPATH</code>: the XPATH for the 'Show more' button to expand the list of required skills in the job offer page.</li>
 <li><code>SKILLS_LIST_CLASSNAME</code>: the CSS class name for the list of required skills in the job offer page.</li>
 <li><code>CLOSE_BUTTON_SKILLS_CSS_SELECTOR</code>: the CSS selector for the close button of the skills list window.</li>

## Disclaimer
<p>This script is for educational and research purposes only. Scraping data from LinkedIn is against the site's terms of service. The user assumes all responsibility for any legal issues that may arise from the use of this script.</p>
