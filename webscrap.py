from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

service = Service()  # ระบุ path ถ้าไม่ได้ใส่ ChromeDriver ใน PATH
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

search_keywords = [
    "วิศวกรรมคอมพิวเตอร์",
    "วิศวกรรมปัญญาประดิษฐ์"
]

all_data = []

for keyword in search_keywords:
    print(f"\n🔎 ค้นหา: {keyword}")
    driver.get("https://mytcas.com")

    # 🔍 ค้นหาช่อง input
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='พิมพ์ชื่อสถาบัน']"))
    )
    search_box.clear()

    # 🧠 ส่งข้อความทีละตัวเพื่อให้เว็บ trigger dropdown
    for char in keyword:
        search_box.send_keys(char)
        time.sleep(0.1)

    # ⏳ รอ dropdown โหลด แล้วกดลง + enter
    time.sleep(1.5)
    search_box.send_keys(Keys.ARROW_DOWN)
    search_box.send_keys(Keys.ENTER)

    # รอโหลดผลลัพธ์
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/programs/']"))
    )
    time.sleep(2)

    program_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/programs/']")
    program_urls = [link.get_attribute("href") for link in program_links]
    print(f"📦 พบ {len(program_urls)} หลักสูตร สำหรับ \"{keyword}\"")

    for url in program_urls:
        try:
            driver.get(url)
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # 🏫 มหาวิทยาลัย
            logo_img = soup.find('img', src=lambda s: s and 'assets.mytcas.com/i/logo' in s)
            university_name = logo_img['alt'] if logo_img and logo_img.has_attr('alt') else 'ไม่พบชื่อมหาวิทยาลัย'

            # 🎓 ชื่อหลักสูตร
            program_dd = soup.find_all('dd')
            program_name_th = program_dd[0].get_text(strip=True) if len(program_dd) >= 1 else 'ไม่พบชื่อหลักสูตร'

            # 💸 ค่าใช้จ่าย
            dt_tag = soup.find('dt', string='ค่าใช้จ่าย')
            dd_tag = dt_tag.find_next_sibling('dd') if dt_tag else None
            tuition_fee = dd_tag.get_text(strip=True) if dd_tag else 'ไม่พบข้อมูลค่าใช้จ่าย'

            # 📍 วิทยาเขต
            dt_campus = soup.find('dt', string='วิทยาเขต')
            dd_campus = dt_campus.find_next_sibling('dd') if dt_campus else None
            campus = dd_campus.get_text(strip=True) if dd_campus else 'ไม่พบข้อมูลวิทยาเขต'

            all_data.append({
                'คำค้น': keyword,
                'ชื่อมหาวิทยาลัย': university_name,
                'ชื่อหลักสูตร': program_name_th,
                'วิทยาเขต': campus,
                'ค่าใช้จ่าย': tuition_fee,
                'ลิงก์': url
            })
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดที่ {url} → {e}")
            continue

# ✅ ปิด browser
driver.quit()

# ✅ บันทึก Excel
df = pd.DataFrame(all_data)
df.to_excel("tcas_multi_keywords.xlsx", index=False)
print("\n✅ ดึงข้อมูลเสร็จและบันทึกลงไฟล์เรียบร้อยแล้ว!")
