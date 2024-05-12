from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import json

chromedriver_path = "/bin/chromedriver"

browser = webdriver.Chrome(service=Service(chromedriver_path))


browser.get("https://www.amazon.com/Best-Sellers/zgbs")

categories = browser.find_elements(By.CSS_SELECTOR, 'div[role="group"] > div[role="treeitem"] a')
all_products = {}
while len(categories) == 0:
	browser.refresh()
	#sometimes it doesnt work. selenium is annoyingly unreliable
	categories = browser.find_elements(By.CSS_SELECTOR, 'div[role="group"] > div[role="treeitem"] a')
category_links = []
for c in categories:
	category_links.append(c.get_attribute("href"))	


#get links to each list
for l in category_links:
	browser.get(l)
	category_name = browser.find_element(By.CSS_SELECTOR, 'div[role="treeitem"] span[class*="style_zg-selected_"]').get_attribute("innerHTML")
	print('now scraping ' + category_name)
	products = []
	while True:
		browser.execute_script("document.querySelector('span.navFooterBackToTopText').scrollIntoView()")
		#items do not all load at once, so script should scroll to bottom before making list
		list_items = browser.find_elements(By.CSS_SELECTOR, '#gridItemRoot')
		try:
			browser.find_element(By.CSS_SELECTOR, 'h4')
			print('there are no best sellers in this category')
			break
		except NoSuchElementException:
			print('', end='')

		impatience = 0
		while len(list_items) < 50 and impatience < 10:
			list_items = browser.find_elements(By.CSS_SELECTOR, '#gridItemRoot')
			time.sleep(1)
			impatience += 1

		for i in list_items:
			try:
				item_rank = i.find_element(By.CSS_SELECTOR, 'span.zg-bdg-text').get_attribute("innerHTML")
				item_name = i.find_element(By.CSS_SELECTOR, 'div[class*="css-line-clamp"]:first-child').get_attribute("innerHTML")
				item_link = i.find_element(By.CSS_SELECTOR, 'a.a-link-normal').get_attribute("href")
				products.append([item_name, item_rank, item_link])
			except NoSuchElementException:
				print('item is missing important information, skipping')
		try:		
			next_page = browser.find_element(By.CSS_SELECTOR, 'li.a-last a').get_attribute('href')
			browser.get(next_page)
		except NoSuchElementException:
			print(str(len(products)) + ' items found')
			#if there is no 'next page' buttons, all items have been scraped
			break

	#there should be 50 items per page
	all_products[category_name] = products


filename = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + '_amazon_top_100_product_lists.json'
with open(filename, 'w') as w:
	w.write(json.dumps(all_products))
print("data saved as " + filename)
time.sleep(1)



