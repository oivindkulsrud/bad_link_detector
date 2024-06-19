import os
import re

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

if __name__ == '__main__':

    directory = '../sykepengesoknad-frontend'

    link_to_file_dict = check_all_source_code_files(directory)
    print(link_to_file_dict)
    # for i in data:
    #     print(i)



