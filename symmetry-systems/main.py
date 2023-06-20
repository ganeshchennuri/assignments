from typing import Any, List
import requests
from bs4 import BeautifulSoup
from constants import aws_docs_url
import json
from topics import create_jsons_for_each_topic


def fetch_documentation_details(aws_docs_url: str) -> List:
    """Fetch documentation web page using requests library
    Parses html output using bs4 library
    Fetches all the topics & their urls (creating topics.json)
    """
    try:
        response = requests.get(aws_docs_url)
        # print(resp.status_code)
        if response.status_code != 200:
            print(f"Error while requesting docs: {response.status_code}")
            return []
        return parse_html_page_create_topics(response.content)
    except Exception as e:
        print(f"Exception Occured: {e}")
        return []


def parse_html_page_create_topics(html_content: Any) -> List:
    """Parses html content and returns list of topics with name & url attributes"""
    soup = BeautifulSoup(html_content, "html.parser")
    highlights = soup.find("div", {"class": "highlights"})
    links = highlights.find_all("a")

    base_url = aws_docs_url.rsplit("/", 1)[0]
    topics = []

    for li in links:
        url = base_url + li["href"].split(".", 1)[1]
        name = li.text.strip()
        topics.append({"name": name, "url": url})

    dump_topics_into_json_file(topics)
    return topics


def dump_topics_into_json_file(topics: List) -> None:
    with open("topics.json", "w") as f:
        json.dump(topics, f, indent=4)


if __name__ == "__main__":
    import time

    start = time.time()

    topics = fetch_documentation_details(aws_docs_url)
    # topics = json.load(open("topics.json", "r"))
    create_jsons_for_each_topic(topics)

    end = time.time()
    print(f"Execution time: {end - start} seconds")
