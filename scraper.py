import selenium.common.exceptions
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_case_data(case_type, case_number, case_year,flash=None):
    """
    Scrapes Delhi High Court portal for orders related to the given case number.
    Returns a dictionary with list of (order_title, date, download_link) and html source of page.
    """
    url = "https://delhihighcourt.nic.in/app/get-case-type-status"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(url)

        # Select case type
        case_type_dropdown = Select(wait.until(EC.presence_of_element_located((By.NAME, "case_type"))))
        case_type_dropdown.select_by_value(case_type)

        # Fill in case number and year
        driver.find_element(By.NAME, "case_number").send_keys(str(case_number))
        year_dropdown = Select(driver.find_element(By.NAME, "case_year"))
        year_dropdown.select_by_value(str(case_year))

        # Extract CAPTCHA
        captcha_text = driver.find_element(By.ID, "captcha-code").text.strip()
        driver.find_element(By.NAME, "captchaInput").send_keys(captcha_text)

        # Submit form
        driver.find_element(By.ID, "search").click()

        # Wait for result to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sorting_1")))

        # Example data scrape (you can tailor this to extract exactly what you need)
        table = driver.find_element(By.ID, "caseTable")
        row = table.find_elements(By.TAG_NAME, "tr")[1]

        result_data = []

        cols = row.find_elements(By.TAG_NAME, "td")
        link = row.find_element(By.XPATH, ".//a[@href]").get_attribute("href")
        result_data.append([col.text.strip() for col in cols])

        driver.get(link)
        doc_links=[]
        dates = []

        while True:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sorting_1")))

            table = driver.find_element(By.ID, "caseTable")
            rows  = table.find_elements(By.TAG_NAME,value="tr")[1:]

            for row in rows:
                doc_links.append(row.find_element(By.TAG_NAME,value='a').get_attribute("href"))
                dates.append(row.find_element(By.CSS_SELECTOR,value="td:nth-of-type(3)").text)

            next_page = driver.find_element(By.CSS_SELECTOR, value="button[aria-label='Next']")

            if "disabled" in next_page.get_attribute("class"):
                break
            else:
                next_page.click()

        final_result = {
            "case_data":result_data[0],
            "doc_links":doc_links,
            "doc_dates":dates
        }

        return final_result,driver.page_source

    except TimeoutException:
        if flash:
            flash("Case information not found, Please try again.", "warning")
        return None

    except selenium.common.exceptions.NoSuchElementException:
        if flash:
            flash("Unexpected page structure: Court site may have changed or blocked access.","warning")
        return None

    except WebDriverException :
        if flash:
            flash(f"WebDriver error (possible network issue)", "warning")
        return None


    except Exception:
        if flash:
            flash(f"Unexpected error", "warning")
        return None

    finally:
            driver.quit()
