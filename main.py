import os
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
# import logging
import json

# Configure logger
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)

LINK_INFO_DICT = {}

def get_text_files(directory, extensions=['.kt', '.tsx', '.ts']):
    text_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                text_files.append(os.path.join(root, file))
    return text_files



def filter_text_files(text_files_path_list):
    patterns_to_filter_out = ["node_modules", "package.json", "package.lock", "yarn.lock", "gradle.kt" ]
    return_list = []
    for i in text_files_path_list:
        can_add = True
        for pattern in patterns_to_filter_out:
            if pattern in i:
                can_add = False
                break
            else:
                continue
        if can_add:
            return_list.append(i)
    return return_list



def get_all_source_code_files(path):
    text_files_list = get_text_files(path)
    return filter_text_files(text_files_list)


def identify_links_in_source_code(text_content):
    """Takes a string and looks for urls starting with https:// or http:// """
    # url_pattern = re.compile(r'https?://\S+')
    # url_pattern = re.compile(r'https://\S+')
    url_pattern = re.compile(r'https://[^\s\'"]+')  # https://chatgpt.com/c/d6ce857a-5791-4c37-ba6c-a619a0fb48f5
    return url_pattern.findall(text_content)



def check_all_source_code_files(path):
    text_files = get_all_source_code_files(path)
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            links = identify_links_in_source_code(content)
            if links:
                print(f'Found links in {file_path}:')
                for link in links:
                    if link in LINK_INFO_DICT:
                        LINK_INFO_DICT[link]['found_in_files'].append(file_path)
                    else:
                        LINK_INFO_DICT[link] = {}
                        LINK_INFO_DICT[link]['found_in_files'] = [file_path]
                    print(link)

    with open('links.json', 'w') as json_file:
        json.dump(LINK_INFO_DICT, json_file, indent=4)

def check_link_in_selenium(link, file_list):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(link)
    except Exception as e:
        print(f'Could not get {link} used in these files: {file_list}. Error: {e}')

    current_url = driver.current_url
    sleep(5)
    print('current_url', current_url)
    scroll_position = driver.execute_script("return window.scrollY")

    LINK_INFO_DICT[link]['scroll_position'] = scroll_position


    current_url_str = str(current_url).replace('https://www.', '').replace('https://', '')
    link_str = link.replace('https://www.', '').replace('https://', '')

    was_redirected = current_url_str != link_str

    if was_redirected:
        LINK_INFO_DICT[link]['redirected_to'] = current_url




# todo the sleep has to be WITH THE ANCH
    if ("#" in link):

        print("anchor found in link")
        link_without_anchor = link.split("#")[0]
        sleep(5)
        driver.get(link_without_anchor)
        scroll_position_without_anchor = driver.execute_script("return window.scrollY")
        LINK_INFO_DICT[link]['link_without_anchor'] = link_without_anchor
        LINK_INFO_DICT[link]['scroll_position_without_anchor'] = scroll_position_without_anchor


        if scroll_position_without_anchor == scroll_position:
            print(f'------ anchor does not matter to scroll position, broken? {link}: used in these files: {file_list}')
            LINK_INFO_DICT[link]['anchor_broken'] = True
        else:
            print(f'anchor works! {link}')





    if was_redirected:
        print(f'!!!!!! Redirected from {link} to {current_url} scroll position: {scroll_position} used in these files: {file_list}')
        LINK_INFO_DICT[link]['redirected'] = True
    else:
        print(f'not redirected: went from {link} to {current_url} scroll position: {scroll_position}')
        LINK_INFO_DICT[link]['redirected'] = False

    driver.quit()

def skip_link(link):
    blacklist = ['cypress', 'localhost', 'uxsignals', 'nextjs', '${', 'nais.io',
               'dev.nav.no', 'github', 'navno.sharepoint', 'tjenester-q1', 'logs.adeo.no', 'flexjar.intern.nav', 'flex-hotjar-emotions', 'amplitude']
    return any(item in link for item in blacklist)


if __name__ == '__main__':

    directory = '../sykepengesoknad-frontend'
    # directory = '../'

    check_all_source_code_files(directory)
    print(LINK_INFO_DICT)
    print("checking directory: ", directory)
    print ("Links found in the source code: ", len(LINK_INFO_DICT))
    counter = 0
    for link in LINK_INFO_DICT:
        if counter > 4:
            break
        if skip_link(link):
            # todo maybe delete here?
            continue
        else:
            counter += 1
            print(f"checking: {link}")
            # print(link)
            check_link_in_selenium(link, LINK_INFO_DICT[link])
    with open('final_result.json', 'w') as json_file:
        json.dump(LINK_INFO_DICT, json_file, indent=4)




