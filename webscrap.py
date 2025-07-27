from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time


# Specify path if ChromeDriver is not in PATH
service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)


# List of search keywords (Thai program names)
search_keywords = [
    "วิศวกรรมคอมพิวเตอร์",
    "วิศวกรรมปัญญาประดิษฐ์"
]


# List to store all extracted data
all_data = []


for keyword in search_keywords:
    print(f"\n🔎 Searching: {keyword}")
    driver.get("https://mytcas.com")

    # Find the input box for searching university/program
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='พิมพ์ชื่อสถาบัน']"))
    )
    search_box.clear()

    # Type the keyword character by character to trigger the dropdown
    for char in keyword:
        search_box.send_keys(char)
        time.sleep(0.1)

    # Wait for dropdown to load, then press down arrow and enter
    time.sleep(1.5)
    search_box.send_keys(Keys.ARROW_DOWN)
    search_box.send_keys(Keys.ENTER)

    # Wait for results to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/programs/']"))
    )
    time.sleep(2)

    program_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/programs/']")
    program_urls = [link.get_attribute("href") for link in program_links]
    print(f"📦 Found {len(program_urls)} programs for \"{keyword}\"")


    for url in program_urls:
        try:
            driver.get(url)
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Extract university name
            logo_img = soup.find('img', src=lambda s: s and 'assets.mytcas.com/i/logo' in s)
            university_name = logo_img['alt'] if logo_img and logo_img.has_attr('alt') else 'University name not found'

            # Extract program name (Thai)
            program_dd = soup.find_all('dd')
            program_name_th = program_dd[0].get_text(strip=True) if len(program_dd) >= 1 else 'Program name not found'

            # Extract tuition fee
            dt_tag = soup.find('dt', string='ค่าใช้จ่าย')
            dd_tag = dt_tag.find_next_sibling('dd') if dt_tag else None
            tuition_fee = dd_tag.get_text(strip=True) if dd_tag else 'Tuition fee not found'

            # Extract campus name
            dt_campus = soup.find('dt', string='วิทยาเขต')
            dd_campus = dt_campus.find_next_sibling('dd') if dt_campus else None
            campus = dd_campus.get_text(strip=True) if dd_campus else 'Campus not found'

            # Append extracted data to the list
            all_data.append({
                'คำค้น': keyword,                # Search keyword
                'ชื่อมหาวิทยาลัย': university_name, # University name
                'ชื่อหลักสูตร': program_name_th,    # Program name (Thai)
                'วิทยาเขต': campus,                # Campus
                'ค่าใช้จ่าย': tuition_fee,         # Tuition fee
                'ลิงก์': url                       # Program URL
            })

        except Exception as e:
            print(f"❌ Error at {url} → {e}")
            continue


# Close the browser after scraping is done
driver.quit()

# Save the results to Excel
df = pd.DataFrame(all_data)
df.to_excel("tcas_data.xlsx", index=False)
print("\n✅ Data scraping complete and file saved successfully!")
