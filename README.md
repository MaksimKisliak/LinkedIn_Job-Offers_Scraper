LinkedIn Job Postings Web Scraper
<p>This is a Python script for web scraping LinkedIn job postings. The script uses Selenium and Beautiful Soup libraries to automate browser actions and parse HTML, respectively.</p>Prerequisites
<ul>
 <li>Python 3.x</li>
 <li><code>pip</code> package installer</li>
 <li>Chrome web browser</li>
 <li>ChromeDriver (matching the Chrome version installed)</li>
</ul>Installation
<ol>
 <li>Clone this repository.</li>
 <li>Install the required Python packages by running <code>pip install -r requirements.txt</code> in the terminal.</li>
 <li>Download ChromeDriver from <a href="https://sites.google.com/a/chromium.org/chromedriver/downloads" rel="nofollow">here</a> and save it in the project directory.</li>
 <li>Configure the environment variables <code>USER_NAME</code>, <code>PASSWORD</code>, and <code>JOB_SEARCH_URL</code>. If running on Railway platform, set <code>RAILWAY_ENVIRONMENT</code> environment variable to <code>1</code>.</li>
</ol>Usage
<p>To run the script, execute <code>python linkedin_job_scraper.py</code> in the terminal. The script will log in to LinkedIn, navigate to the job search URL, scrape the job postings, and save the data to a CSV file named <code>job_offers.csv</code>.</p>Disclaimer
<p>This script is for educational and research purposes only. Scraping data from LinkedIn is against the site's terms of service. The user assumes all responsibility for any legal issues that may arise from the use of this script.</p>
