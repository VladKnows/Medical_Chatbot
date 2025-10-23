import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_links(driver_path="data/msedgedriver.exe", headless=True):
    edge_options = Options()
    if headless:
        edge_options.add_argument("--headless")

    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        driver.get("https://www.mayoclinic.org/diseases-conditions")
        wait = WebDriverWait(driver, 5)
        section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cmp-alphabet-facet--inner"))
        )
        letter_links = [a.get_attribute("href") for a in section.find_elements(By.TAG_NAME, "a")]

        diseases = []

        def extract_diseases_from_letter(link):
            driver.get(link)
            wait = WebDriverWait(driver, 5)
            try:
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cmp-result-name__link"))
                )
            except TimeoutException:
                return []

            result = [(el.text.strip(), el.get_attribute("href")) for el in elements]
            return result

        for l in letter_links:
            diseases.extend(extract_diseases_from_letter(l))

        return diseases

    finally:
        driver.quit()


def save_illness_links(diseases, filename="illness_links.json"):
    filename = "data/" + filename
    illness_links = json.dumps(diseases, indent=4)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(illness_links)


def extract_illness_details(link, driver_path="data/msedgedriver.exe", headless=True):
    edge_options = Options()
    if headless:
        edge_options.add_argument("--headless")

    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        driver.get(link)
        wait = WebDriverWait(driver, 5)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except TimeoutException:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")

        illness = {}
        illness["Name of illness"] = soup.find("h1").get_text(strip=True)

        def extract_list(h2_text):
            header = soup.find("h2", string=lambda s: s and h2_text.lower() in s.lower())
            items = []
            if not header:
                return items

            for sibling in header.find_next_siblings():
                if sibling.name in ("h2", "h3"):
                    break

                if sibling.name == "ul":
                    for li in sibling.find_all("li"):
                        strong = li.find("strong")

                        if "risk" in h2_text.lower() and strong and any(
                                kw in strong.get_text(strip=True).lower() for kw in ["age", "sex"]
                        ):
                            text = li.get_text(strip=True)
                            if "." in text:
                                text = text.split(".", 1)[1].strip()
                            items.append(text)

                        elif strong:
                            items.append(strong.get_text(strip=True))

                        else:
                            items.append(li.get_text(strip=True))

                    break

            if not items:
                for sibling in header.find_next_siblings():
                    if sibling.name in ("h2", "h3"):
                        break

                    if sibling.name == "p":
                        paragraph = sibling.get_text(strip=True)
                        items.append(paragraph)
                        break

            if not items:
                p_fallback = header.find_next("p")
                if p_fallback:
                    paragraph = p_fallback.get_text(strip=True)
                    if paragraph != "":
                        items.append(paragraph)

            return items

        illness["Symptoms"] = extract_list("Symptoms")
        illness["Causes"] = extract_list("Causes")
        illness["Risk Factors"] = extract_list("Risk factors")
        illness["Complications"] = extract_list("Complications")
        illness["Prevention"] = extract_list("Prevention")

        overview_header = soup.find("h2", string=lambda s: s and "Overview" in s)
        overview_text = ""
        if overview_header:
            sibling = overview_header.find_next_sibling()
            while sibling:
                if sibling.name == "h2":
                    break
                if sibling.name == "p":
                    overview_text += sibling.get_text(strip=True) + " "
                sibling = sibling.find_next_sibling()
        illness["Overview"] = overview_text.strip()

        return illness

    finally:
        driver.quit()


def extract_all_illness_details(input_file="illness_links.json", output_file="illness_details.json"):
    input_file = "data/" + input_file
    output_file = "data/" + output_file

    with open(input_file, "r", encoding="utf-8") as f:
        illness_links = json.load(f)

    illness_details = []

    for i, (name, link) in enumerate(illness_links):
        print(f"[{i+1}/{len(illness_links)}] Extracting details for: {name}")
        details = extract_illness_details(link)
        details["URL"] = link
        illness_details.append(details)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(illness_details, f, indent=4, ensure_ascii=False)