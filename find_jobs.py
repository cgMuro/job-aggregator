import csv
import bs4
from selenium import webdriver

# Variables
DRIVER_PATH = '/Users/gioele/Downloads/chromedriver'
URL = 'https://www.indeed.co.uk'
JOB = input('What? (job title, keywords, company)\n')
WHERE = input('Where? (city, postcode)\n')
HOW_MANY_PAGES = int(input('How many pages do you want to scan?\n'))
# Filter variables
JOB_TYPE = input("Job type (Permanent, Full-time, Contract, Temporary, Part-time, Intership, Appreticeship, Volunteer, ''):\n")
PROGRAMMING_LANGUAGE = input('Programming language:\n')
DATE_POSTED = input("Date posted (Last 24 hours, Last 3 days, Last 7 days, Last 14 days, ''):\n")


# Find job posts function
def find_jobs(driver):
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')

    jobs = soup.find_all(class_='jobsearch-SerpJobCard')

    jobs_list = []

    for job in jobs:
        job_title = job.find(class_='title').find('a').getText()
        company_name = job.find(class_='sjcl').find('div').find(class_='company').text
        summary = [i.text for i in job.find(class_='summary').find('ul').find_all('li')] if job.find(class_='summary').find('ul') else job.find(class_='summary').text
        link = URL + str(job.find(class_='title').find('a').get('href'))

        jobs_list.append({'job_title': job_title, 'company_name': company_name, 'summary': summary, 'link': link})

    save_jobs(jobs_list)

def save_jobs(jobs):
    type_of_save = input('Do you want to save the jobs found into a text file or a csv file? (txt/csv) ')

    if type_of_save == 'txt':
        # Save as a text file
        with open('jobs.txt', 'w') as f:
            f.write('Jobs for ' + JOB.upper() + ' in ' + WHERE.upper() + '\n\n\n')
            
            idx = 0
            while idx <= (len(jobs) - 1):
                # Save jobs to file
                job = jobs[idx]
                f.write('Job Title: ' + job['job_title'].strip()+ '\n')
                f.write('Company Name: ' + job['company_name'].strip() + '\n')
                f.write('Summary:\n')
                for i in job['summary']:
                    f.write(f' - {i}\n')
                f.write('Link: ' + job['link'] + '\n\n\n')

                # Incerement index
                idx += 1

    elif type_of_save == 'csv':
        # Save as a csv file
        with open('jobs.csv', 'w') as csv_file:
            fieldnames = ['Job Title', 'Company Name', 'Summary', 'Link']
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            idx = 0
            while idx <= (len(jobs) - 1):
                # Save jobs to file
                job = jobs[idx]
                csv_writer.writerow({'Job Title': job['job_title'].strip(), 'Company Name': job['company_name'].strip(), 'Summary': [i for i in job['summary']], 'Link': job['link']})
                
                # Incerement index
                idx += 1

    else:
        save_jobs(jobs)
    

# Filter jobs function
def filter_jobs(driver):
    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')

    # Job type
    job_type_button = driver.find_element_by_css_selector('#filter-job-type > button')
    job_type_button.click()
    job_type_choices = driver.find_elements_by_css_selector('#filter-job-type-menu .rbLabel')
    for span in job_type_choices:
        if span.text == JOB_TYPE:
            span.click()
            break

    # Programming Language
    try:
        programming_language_button = driver.find_element_by_css_selector('#filter-taxo1 > button')
        programming_language_button.click()
        p_l_choices = driver.find_elements_by_css_selector('#filter-taxo1-menu .rbLabel')
        for span in p_l_choices:
            if span.text == PROGRAMMING_LANGUAGE:
                span.click()
                break
    except:
        pass
    
    # Date posted
    date_button = driver.find_element_by_css_selector('#filter-dateposted > button')
    date_button.click()
    date_choices = driver.find_elements_by_css_selector('#filter-dateposted-menu .rbLabel')
    for span in date_choices:
        if span.text == DATE_POSTED:
            span.click()
            break


print('Starting...')

driver = webdriver.Chrome(DRIVER_PATH)

driver.get(URL)

# Complete and submit the form
job_input = driver.find_element_by_css_selector('#text-input-what')
where_input = driver.find_element_by_css_selector('#text-input-where')

job_input.send_keys(JOB)
where_input.send_keys(WHERE)

where_input.submit() # Sumbit form

# Filter jobs
filter_jobs(driver)

print('\nGetting jobs from page 1...\n')

# Find jobs
find_jobs(driver)

# Run the script again if the more than the first page is requested
if HOW_MANY_PAGES > 1:
    for page in range(1, HOW_MANY_PAGES):
        # Change page and get the jobs in the new page
        driver.get(f"{URL}/jobs?q={JOB.replace(' ', '+')}&l={WHERE.replace(' ', '+')}&start={str(page * 10)}")
        print(f'\nGetting jobs from page {page+1}...\n')
        find_jobs(driver)

print('\nFinished.')