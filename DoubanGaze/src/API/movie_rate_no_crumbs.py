from urllib.parse import quote
from bs4 import BeautifulSoup
import requests
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

def get_movie_id(search_query: str) -> str:
    """get movie id from "https://movie.douban.com"

    Args:
        search_query (str): enter the movie name

    Returns:
        item_id, item_title, item_url (tuple with 3 strings)
    """
    encoded_query = quote(search_query)

    add_tags_url = f"https://movie.douban.com/j/subject_suggest?q={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    params = {
        "q": search_query
    }

    response = requests.get(add_tags_url, headers=headers, params=params)

    if response.status_code == 200:
        try:
            search_result = response.json()
            print(json.dumps(search_result, indent=4, ensure_ascii=False))
            if search_result:
                first_result = search_result[0]
                item_id = first_result["id"]
                item_title = first_result["title"]
                item_url = f"https://movie.douban.com/subject/{item_id}/"
                print(f"Movie ID: {item_id}")
                print(f"Movie URL: {item_url}")
                return item_id, item_title, item_url
            else:
                print("found no info")
                return None, None, None
        except json.JSONDecodeError as e:
            print(f"parse json failed")
            print(f"original response: {response.text}")
            return None
    else:
        print(f"requests failed❌, status code: {response.status_code}")
        print(response.text) 
        return None

def get_movie_rate(item_url):
    """get movie rating and movie_rating_count

    Args:
        item_url (str): returned movie url from get_movie_id

    Returns:
        movie_rating, movie_rating_count(tuple with 2 strings)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    response = requests.get(item_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    if soup:
        try:
            movie_rating_element = soup.select_one("div.rating_self.clearfix > strong")
            movie_rating_count_element = soup.select_one("div.rating_sum a > span")
            if movie_rating_element and movie_rating_count_element:
                movie_rating = movie_rating_element.text.strip()
                movie_rating_count = movie_rating_count_element.text.strip()
                print(f"RATING: {movie_rating} ⭐")
                print(f"RATING NUM: {movie_rating_count} 🤺")
                return movie_rating, movie_rating_count
            else:
                return None, None
        except Exception as e:
            print(f"Error when crawl: {e}")
    else:
        print(f"requests failed❌, status code: {response.status_code}")
    

if __name__ == "__main__":

    search_query = "上载新生 第一季" # TODO

    # start timing ⏳
    start_time = time.perf_counter()

    item_id, item_title, item_url = get_movie_id(search_query)

    get_movie_rate(item_url)

    # stop timing ⌛
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    logging.debug(f"Fetching time: {elapsed_time:.2f} s ⏱️")
