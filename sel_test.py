import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def input_word(word):
	driver = webdriver.Firefox()
	driver.get(f'https://translate.google.com/?sl=en&tl=ru&text={word}&op=translate')
	WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME,'mvqA2c'))).click()
	trans_list = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'Q4iAWc')))
	result = trans_list[0].text
	return result



if __name__ == "__main__":
	with open('input_words.csv') as f:
		reader = csv.reader(f)
		for row in reader:
			if row[1] == input_word(row[0]):
				print('successfully')
			else:
				print(f'failed, result:{input_word(row[0])}, expected result:{row[1]}')

