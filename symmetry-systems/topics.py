import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
from typing import Any, List, Dict


def create_jsons_for_each_topic(topics: List) -> None:
    if not topics:
        print("Topic List is empty")
        return
    with concurrent.futures.ThreadPoolExecutor() as executor:
        _ = executor.map(parse_url_and_create_json_with_html_content, topics)


def parse_url_and_create_json_with_html_content(topic: Dict) -> None:
    if html_content := fetch_html_response_from_url(topic["url"]):
        soup = BeautifulSoup(html_content, "html.parser")

        output_data = {"prefix": soup.find("code").text, "link": [topic["url"]]}

        tables = soup.find_all("table")

        for table in tables:
            text = table.find("th").text
            if text == "Actions":
                output_data["actions"] = create_actions_json_data_from_table(table)
            elif text == "Resource types":
                output_data["resources"] = create_resources_json_data_from_table(table)
            elif text == "Condition keys":
                output_data["conditions"] = create_conditions_json_data_from_table(
                    table
                )

        with open(f"output_jsons/{output_data['prefix']}.json", "w") as f:
            json.dump(output_data, f, indent=4)
    else:
        print("Could not get the response from the aws docs")


def fetch_all_rows_from_table(table_data: Any) -> List:
    # Fetching all rows from the table & leaving header
    rows = table_data.find_all("tr")
    return rows[1:]


def create_actions_json_data_from_table(actions_table: Any) -> List:
    actions_data = []

    rows = fetch_all_rows_from_table(actions_table)

    for row in rows:
        # fetching all columns from the row
        tds = row.find_all("td")

        if len(tds) == 6:
            actions_data.append(
                {
                    "action": tds[0].find("a").text
                    if tds[0].find("a").text
                    else tds[0].find_all("a")[-1].text,
                    "access": tds[2].text.strip(),
                    "resources": [tds[3].text.strip()] if tds[3].text else [],
                    "conditionKeys": [tds[4].text.strip()] if tds[4].text else [],
                    "dependentActions": [tds[5].text.strip()] if tds[5].text else [],
                    "desc": tds[1].text,
                }
            )
        elif len(tds) == 3:
            actions_data.append(
                {
                    "action": actions_data[-1]["action"],
                    "access": actions_data[-1]["access"],
                    "resources": [tds[0].text.strip()] if tds[0].text else [],
                    "conditionKeys": [item.text for item in tds[1].find_all("a")],
                    "dependentActions": [tds[2].text.strip()] if tds[2].text else [],
                    "desc": actions_data[-1]["desc"],
                }
            )

    return actions_data


def create_resources_json_data_from_table(resources_table: Any) -> List:
    resources_data = []

    rows = fetch_all_rows_from_table(resources_table)

    for row in rows:
        # fetching all columns from the row
        tds = row.find_all("td")
        resources_data.append(
            {
                "resourceType": tds[0].find("a").text
                if tds[0].find("a").text
                else tds[0].find_all("a")[-1].text,
                "arn": tds[1].text.strip(),
                "conditionKeys": [tds[2].text.strip()] if tds[2].text else [],
            }
        )
    return resources_data


def create_conditions_json_data_from_table(conditions_table: Any) -> List:
    conditions_data = []
    rows = fetch_all_rows_from_table(conditions_table)

    for row in rows:
        # fetching all columns from the row
        tds = row.find_all("td")
        conditions_data.append(
            {
                "conditionKey": tds[0].text.strip(),
                "desc": tds[1].text.strip(),
                "typ": tds[2].text.strip(),
            }
        )
    return conditions_data


def fetch_html_response_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error while requesting docs: {response.status_code}")
            return ""
        return response.text
    except Exception as e:
        print(f"Exception Occured: {e}")
        return ""
