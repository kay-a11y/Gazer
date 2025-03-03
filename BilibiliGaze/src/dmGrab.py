import requests
from bs4 import BeautifulSoup
from xml.dom import minidom
import json
import re
import os
import time
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# ------------------------- CONST ------------------------ #
FOLDER_PATH = r"E:\Gazer\BilibiliGaze\data" # TODO default saving folder
# ------------------------- CONST ------------------------ #

def get_cid(url):
    """get cid from `window.__playinfo__` in HTML

    Args:
        url (str): direct link to Bilibili video

    Returns:
        cid (str): video cid
    """
    headers = {
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    play_info_match = re.search(r'window\.__playinfo__\s*=\s*({.*?"video":.*?"audio":.*?"session":.*?})\s*', response.text)

    # initialize cid 
    cid = None

    if play_info_match:
        try:
            play_info = json.loads(play_info_match.group(1))
            cid = play_info['data']['dash']['video'][0]['baseUrl'].split('/')[6]
            logging.info(f'cid = {cid} 📺')
            return cid
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"parse play_info FAILED: {e} ❌")
            return None
    else:
        print("window.__playinfo__ NOT FOUND ❓")
    return None

def get_xml(cid):
    """parse xml page based on cid string

    Args:
        cid (str): video cid, returned from `get_cid`

    Returns:
        soup (BeautifulSoup): BeautifulSoup object

    Raises:
        requests.exceptions.RequestException: if HTTP request failed
        Exception: if failed to parse XML
    """
    xml_url = f"https://comment.bilibili.com/{cid}.xml"
    logging.info(f"xml_url = {xml_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
    }

    try:
        response = requests.get(xml_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content.decode('utf-8'), features="xml")
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request failed ❌: {e}")
        return None
    except Exception as e:
        logging.error(f"XML parse failed ❌: {e}")
        return None

def ensure_directory_exists(path):
    """Ensure that the directory exists; create it if it does not.

    Args:
        path (str): directory path
    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logging.error(f"Failed to create directory {path}: {e}")
        raise

def write_xml(soup, file_name):
    """write BeautifulSoup object to xml file

    Args:
        soup (BeautifulSoup): BeautifulSoup object including XML data
        file_name (str): XML file name (includes extension)
    Returns:
        xml_path (str): XML file saving path
    """
    target_path = os.path.join(FOLDER_PATH, 'raw', 'comment')
    xml_path = os.path.join(target_path, file_name)

    try:
        ensure_directory_exists(target_path)

        xml_string = soup.prettify() 
        dom = minidom.parseString(xml_string) 
        pretty_xml = dom.toprettyxml(indent="   ") 

        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        logging.info(f"XML SAVED in 📂: {xml_path}")
        return xml_path
    except Exception as e:
        logging.error(f"Fail to save XML 💦: {e}")
        return None

def block_shits(xml_path, words=None):
    """delete assigned block words in xml file

    Args:
        xml_path (str): xml file path
        words (list, optional): blocked words list. Defaults to None.

    Returns:
        cleaned_content (str): a clean file content
    """
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        for line in lines:
            should_keep = True 
            if words:
                for word in words:
                    if word in line:
                        should_keep = False 
                        break 
            if should_keep:
                cleaned_lines.append(line)
        
        cleaned_content = ''.join(cleaned_lines)

        target_path = os.path.join(FOLDER_PATH, 'processed', 'comment')
        ensure_directory_exists(target_path)

        clean_xml_filename = f"clean_{os.path.basename(xml_path)}"
        clean_xml_path = os.path.join(target_path, clean_xml_filename)
        
        with open(clean_xml_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        logging.info(f"XML CLEANED in 📂: {clean_xml_path}")
        return clean_xml_path
    except FileNotFoundError:
        print(f"ERROR: XML file {xml_path} not found ❓")
        return None
    except Exception as e:
        print(f"ERROR when clean blocked words in XML file {xml_path} ❌")


if __name__ == '__main__':
    url = "https://www.bilibili.com/video/BV1fm4y1y7SJ/?spm_id_from=333.788.top_right_bar_window_history.content.click&vd_source=8442209456a10c982626f270cd3d9b7c" # TODO

    file_name = 'dan_mu.xml'   # TODO: XML file name
    words = ['啊啊啊', '滚', '吵']  # TODO: Add blocked words

    # start timing ⏳
    start_time = time.perf_counter()

    cid = get_cid(url)
    logging.debug(f"cid = {cid}")

    soup = get_xml(cid)

    if soup:
        xml_path = write_xml(soup, file_name)

    block_shits(xml_path, words=None)

    # stop timing ⌛
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    logging.debug(f"Fetching time: {elapsed_time:.2f} s ⏱️")
