import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


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

link_to_file_dict = {}

def check_all_source_code_files(path):
    text_files = get_all_source_code_files(path)
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            links = identify_links_in_source_code(content)
            if links:
                print(f'Found links in {file_path}:')
                for link in links:
                    if link in link_to_file_dict:
                        link_to_file_dict[link].append(file_path)
                    else:
                        link_to_file_dict[link] = [file_path]
                    print(link)

    return link_to_file_dict

def open_link_in_selenium(link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(link)
    current_url = driver.current_url


    current_url_str = str(current_url).replace('https://www.', '').replace('https://', '')
    link_str = link.replace('https://www.', '').replace('https://', '')

    if current_url_str != link_str:
        print(f'- [ ] Redirected from {link} to {current_url}')
    else:
        pass

    driver.quit()

if __name__ == '__main__':

    # directory = '../sykepengesoknad-frontend'
    directory = '../spinnsyn-frontend'
    # directory = '../ditt-sykefravaer'
    directory = '../'

    link_to_file_dict = check_all_source_code_files(directory)
    print(link_to_file_dict)
    print("checking directory: ", directory)
    print ("Links found in the source code: ", len(link_to_file_dict))
    for link in link_to_file_dict:
        if 'cypress' in link or 'localhost' in link or 'uxsignals' in link or 'nextjs' in link \
                or "${" in link or 'nais.io' in link or 'dev.nav.no' in link or 'github' in link \
                or 'navno.sharepoint' in link or "tjenester-q1" in link or "logs.adeo.no" in link:
            continue
        # print(link)
        open_link_in_selenium(link)




