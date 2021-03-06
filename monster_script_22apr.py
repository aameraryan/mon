from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys
import csv
import datetime

file_name = input('Enter file name : ')

errors = 0
total_count = 0

#   fieldnames section

first_fieldnames = ['name', 'resume_id', 'education', 'location', 'total_experience',
                    'notice_period', 'designation', 'company', 'current_ctc', 'heading',
                    'roles', 'functions', 'skills', 'industry', 'pre_location',
                    'nationality', 'active_on', 'updated_on', 'link']
profile_fieldnames = first_fieldnames + ['phone', 'email', 'extra_details']

#   fieldnames section end


#   files writers and readers

try:
    all_data_csv = open('all_data_csv.csv', 'r')
except:
    all_data_csv = open('all_data_csv.csv', 'a')

all_csv_reader = csv.DictReader(all_data_csv)

try:
    all_resume_id = [row.get('resume_id') for row in all_csv_reader]
except:
    all_resume_id = []

csv_file = open(file_name + '-{}.csv'.format(datetime.date.today()), 'a', newline='')
writer = csv.DictWriter(csv_file, fieldnames=first_fieldnames)
writer.writeheader()

#   files section ends


#   driver section

driver = webdriver.Chrome('chromedriver.exe')
login_url = 'https://recruiter.monsterindia.com/'
driver.get(login_url)
abc = input('Press Enter After Making Filters. Make sure resume list is showing : ')

#   driver section ends


def get_profiles():
    count = 0
    p_errors = 0
    p_csv_file = open((file_name + '.csv'), 'r')
    p_new_file = open(('Final-' + file_name + '.csv'), 'w', newline='')
    p_writer = csv.DictWriter(p_new_file, fieldnames=profile_fieldnames)
    all_data_csv = open('all_data_csv.csv', 'a', newline='')
    all_csv_writer = csv.DictWriter(all_data_csv, fieldnames=profile_fieldnames)
    p_writer.writeheader()
    p_reader = csv.DictReader(p_csv_file)
    time.sleep(2)
    for row in p_reader:
        link = row.get('link')
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            phone = soup.find('span', {'class': 'mob_container'}).text.replace('-', '').replace('=', '').strip()
        except:
            phone = '-'
        try:
            email_div = driver.find_element_by_xpath(
                '/html/body/div[1]/div[3]/div[2]/div[1]/div/div/div[1]/div[1]').text
            email = email_div
            if '\n' in email_div:
                for raw_email in email_div.split('\n'):
                    if '@' in raw_email:
                        email = raw_email
                        pass
        except:
            email = '-'
        try:
            extra_details = soup.find('div', {'class': 'skr_basicinfo_other'}).text.replace('\n', '').replace('\t',
                                                                                                              '').replace(
                '  ', '').strip()
        except:
            extra_details = '-'

        new_dict = {'phone': phone, 'email': email, 'extra_details': extra_details}
        new_dict_valid = [True if new_dict[i] == '-' else False for i in new_dict]
        if all(new_dict_valid):
            input('check for captcha')
        my_dict = dict(row)
        my_dict.update(new_dict)
        try:
            p_writer.writerow(my_dict)
            all_csv_writer.writerow(my_dict)
            ##            print(count, '-', my_dict)
            print(count)
            count += 1
        except Exception as e:
            print('main exception : ', e)
            p_errors += 1
            print('-----', p_errors)
    time.sleep(2)
    print('Total Errors : ', p_errors)


def page_changer(page_number):
    try:
        current_page = int(driver.find_elements_by_xpath("//div[@class='left srinactivenew sractivenew']")[-1].text.strip())
        if current_page != page_number:
            if page_number % 5 != 1:
                driver.find_elements_by_xpath("//div[@onclick='goToPage({});']".format(page_number))[-1].click()
            else:
                driver.find_elements_by_xpath("//a[@href='javascript:goToPage({});']".format(page_number))[-1].click()
    except Exception as e:
        print(e)
        input('Click to page {} and press ENTER : '.format(page_number))


def page_160_resumes():
    try:
        driver.find_element_by_xpath("//div[@id='res_dpidtop_id']").click()
        driver.find_element_by_xpath("//a[@class='option_item'][@data-value='res_dpidtop'][@data-id='160']").click()
    except:
        input("Press 160 resumes button : ")


def page_scroller():
    time.sleep(0.5)
    html = driver.find_element_by_tag_name('html')
    html.send_keys(Keys.END)
    time.sleep(0.5)


def get_page(no_of_pages):
    global errors, total_count

    page_160_resumes()
    time.sleep(3)

    for page_number in range(1, no_of_pages):
        time.sleep(3)
        page_changer(page_number)
        time.sleep(3)
        print(page_number, no_of_pages)
        page_scroller()
        time.sleep(3)

        resumes = driver.find_elements_by_class_name('resumeitem_Section')
        print(len(resumes))
        for resume in resumes:
            try:
                name = resume.find_element_by_class_name('namepro').text.strip()
            except:
                name = '--'
            try:
                resume_id = str(resume.get_attribute('id')).replace('row1_', '')
            except:
                resume_id = '--'
            try:
                heading = resume.find_element_by_class_name('res_h').text
            except:
                heading = '--'
            try:
                raw_link = resume.find_element_by_class_name('res_h').get_attribute('href')
                link = raw_link[:raw_link.find(';', raw_link.find('uid'))]
            except:
                link = '--'
            try:
                designation = resume.find_element_by_class_name('desig_sftlnk').text
            except:
                designation = '--'
            try:
                company = resume.find_element_by_id('company' + resume_id).text.replace('@', '').strip()
            except:
                company = '--'
            try:
                location = resume.find_element_by_class_name('info_loc').text
            except Exception as e:
                print(e)
                location = '---'
            try:
                nationality = resume.find_element_by_class_name('nationality').text
            except:
                nationality = '--'
            try:
                first_header = list(
                    resume.find_element_by_class_name('profile_profess').find_elements_by_tag_name('div'))
                notice_period = first_header[0].text.split('\n')[1]
                total_experince = first_header[1].text.split('\n')[1]
                current_ctc = first_header[2].text.split('\n')[1]
            except Exception as e:
                notice_period = '--'
                total_experince = '--'
                current_ctc = '--'
                print(e)
            try:
                skills = resume.find_element_by_id('key_skills' + resume_id).text
            except:
                skills = '--'
            try:
                pre_location = resume.find_element_by_id('preloc' + resume_id).text
            except:
                pre_location = '--'
            try:
                education = resume.find_element_by_id('edu' + resume_id).text
            except:
                education = '--'
            try:
                industry = resume.find_element_by_id('rind' + resume_id).text
            except:
                industry = '--'
            try:
                functions = resume.find_element_by_id('rcat' + resume_id).text
            except:
                functions = '--'
            try:
                roles = resume.find_element_by_id('rrol' + resume_id).text
            except:
                roles = '--'
            try:
                info = resume.find_element_by_class_name('resumeitem_footer').find_element_by_class_name(
                    'textfoot').text.strip()
                info_list = info.split('|')
                active_on = info_list[0].replace('Active on: ', '').strip()
                updated_on = info_list[1].replace('Updated: ', '').strip()
            except Exception as e:
                print('Active : ', e)
                active_on = '--'
                updated_on = '--'

            my_dict = {'name': name, 'resume_id': resume_id, 'education': education, 'location': location,
                       'total_experience': total_experince, 'notice_period': notice_period, 'designation': designation,
                       'company': company, 'current_ctc': current_ctc, 'heading': heading, 'roles': roles,
                       'functions': functions, 'skills': skills, 'industry': industry, 'pre_location': pre_location,
                       'nationality': nationality, 'active_on': active_on, 'updated_on': updated_on, 'link': link}
            if resume_id not in all_resume_id:
                try:
                    writer.writerow(my_dict)
                    total_count += 1
                except:
                    errors += 1
                    print(errors)
            else:
                print('Duplicate -> ', my_dict)
            print(resume_id)


def get_page_folder(no_of_pages):
    global errors, total_count

    page_160_resumes()

    for page_number in range(1, no_of_pages):
        page_changer(page_number)
        page_scroller()

        resumes = driver.find_elements_by_class_name('resumeitem_Section')
        print(len(resumes))
        for resume in resumes:
            try:
                name = resume.find_element_by_class_name('namepro').text.strip()
            except:
                name = '--'
            try:
                resume_id = str(resume.get_attribute('id')).replace('row1_', '')
            except:
                resume_id = '--'
            try:
                heading = resume.find_element_by_class_name('res_h').text
            except:
                heading = '--'
            try:
                raw_link = resume.find_element_by_class_name('res_h').get_attribute('href')
                link = raw_link[:raw_link.find(';', raw_link.find('uid'))]
            except:
                link = '--'
            try:
                designation = resume.find_element_by_id('desig').text
            except:
                designation = '--'
            try:
                company = resume.find_element_by_id('company').text.replace('@', '').strip()
            except:
                company = '--'
            try:
                location = resume.find_element_by_class_name('info_loc').text
            except:
                location = '--'
            try:
                nationality = resume.find_element_by_class_name('nationality').text
            except:
                nationality = '--'
            try:
                first_header = list(
                    resume.find_element_by_class_name('profile_profess').find_elements_by_tag_name('div'))
                notice_period = first_header[0].text.split('\n')[1]
                total_experince = first_header[1].text.split('\n')[1]
                current_ctc = first_header[2].text.split('\n')[1]
            except Exception as e:
                notice_period = '--'
                total_experince = '--'
                current_ctc = '--'
                print(e)

            skills, pre_location, education, industry, roles, functions = '--', '--', '--', '--', '--', '--'

            try:
                info_soup = BeautifulSoup(resume.find_element_by_class_name('profile_skill').get_attribute('innerHTML'),
                                          'lxml')
                for info_type in info_soup.find_all('div', {'class': 'skillType'}):
                    info_type_text = info_type.text.strip()
                    print(info_type_text)
                    print(info_type.findNext('div').text)
                    if 'Skills' in info_type_text:
                        skills = info_type.findNext('div').text.strip()
                    elif 'Location' in info_type_text:
                        pre_location = info_type.findNext('div').text.strip()
                    elif 'Education' in info_type_text:
                        education = info_type.findNext('div').text.strip()
                    elif 'Industry' in info_type_text:
                        industry = info_type.findNext('div').text.strip()
                    elif 'Function' in info_type_text:
                        functions = info_type.findNext('div').text.strip()
                    elif 'Role' in info_type_text:
                        roles = info_type.findNext('div').text.strip()

            except Exception as e:
                print(e)
                pass

            try:
                info = resume.find_element_by_class_name('resumeitem_footer').find_element_by_class_name(
                    'textfoot').text.strip()
                info_list = info.split('|')
                active_on = info_list[0].replace('Active on: ', '').strip()
                updated_on = info_list[1].replace('Updated: ', '').strip()
            except Exception as e:
                print('Active : ', e)
                active_on = '--'
                updated_on = '--'

            my_dict = {'name': name, 'resume_id': resume_id, 'education': education, 'location': location,
                       'total_experience': total_experince, 'notice_period': notice_period, 'designation': designation,
                       'company': company, 'current_ctc': current_ctc, 'heading': heading, 'roles': roles,
                       'functions': functions, 'skills': skills, 'industry': industry, 'pre_location': pre_location,
                       'nationality': nationality, 'active_on': active_on, 'updated_on': updated_on, 'link': link}
            if resume_id not in all_resume_id:
                try:
                    writer.writerow(my_dict)
                    total_count += 1
                    ##print(total_count, '-> ', my_dict)
                except:
                    errors += 1
                    print(errors)
            else:
                print('Duplicate -> ', my_dict)

    csv_file.close()
    all_data_csv.close()
    get_profiles()


task = int(input('Press 1 for Search | 2 for Folder : '))
no_of_pages = (int(input("Enter no of resumes to save : ")) // 160) + 1
if task == 1:
    get_page(no_of_pages=no_of_pages)
elif task == 2:
    get_page_folder(no_of_pages=no_of_pages)

input('Logout : ')
driver.close()
print('Total Errors : ', errors)
