from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# ✅ Edge driver path
edge_driver_path = ''
options = webdriver.EdgeOptions()
options.use_chromium = True
driver = webdriver.Edge(service=Service(edge_driver_path), options=options)

# ✅ ค้นหา "วิศวกรรมคอมพิวเตอร์"
driver.get("https://mytcas.com")
search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='พิมพ์ชื่อสถาบัน']"))
)
search_box.send_keys("วิศวกรรมคอมพิวเตอร์")
time.sleep(1)
search_box.send_keys(Keys.ARROW_DOWN)
search_box.send_keys(Keys.ENTER)

# ✅ รอโหลดผลลัพธ์
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/programs/']"))
)
time.sleep(2)

# ✅ ดึงลิงก์ของแต่ละหลักสูตร
program_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/programs/']")
program_urls = [link.get_attribute("href") for link in program_links]

print(f"📦 พบหลักสูตร {len(program_urls)} รายการ เตรียมดึงข้อมูล...")

data = []

# ✅ วนเข้าไปดึงข้อมูลจากแต่ละหลักสูตร
for url in program_urls:
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 🏫 ชื่อมหาวิทยาลัย
    university_name = 'ไม่พบชื่อมหาวิทยาลัย'
    logo_img = soup.find('img', src=lambda s: s and 'assets.mytcas.com/i/logo' in s)
    if logo_img and logo_img.has_attr('alt'):
        university_name = logo_img['alt']

    # 🎓 ชื่อหลักสูตร
    program_name_th = 'ไม่พบชื่อหลักสูตร'
    program_dd = soup.find_all('dd')
    if len(program_dd) >= 1:
        program_name_th = program_dd[0].get_text(strip=True)

    # 💸 ค่าใช้จ่าย
    tuition_fee = 'ไม่พบข้อมูลค่าใช้จ่าย'
    dt_tag = soup.find('dt', string='ค่าใช้จ่าย')
    if dt_tag:
        dd_tag = dt_tag.find_next_sibling('dd')
        if dd_tag:
            tuition_fee = dd_tag.get_text(strip=True)

    data.append({
        'ชื่อมหาวิทยาลัย': university_name,
        'ชื่อหลักสูตร': program_name_th,
        'ค่าใช้จ่าย': tuition_fee,
        'ลิงก์': url
    })

# ✅ ปิด browser
driver.quit()

# ✅ สร้าง DataFrame แล้วบันทึก Excel
df = pd.DataFrame(data)
output_path = 'tcas_computer_engineering.xlsx'
df.to_excel(output_path, index=False)
print(f"\n✅ บันทึกข้อมูลเรียบร้อยแล้ว: {output_path}")
