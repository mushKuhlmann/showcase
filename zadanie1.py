import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#создаем функцию, в качестве аргумента слово в неправильной раскладке.
def input_word(word):
	driver = webdriver.Firefox()
#открываем ссылку с указанием языка источника и языка перевода, и сразу вставляем аргумент
	driver.get(f'https://translate.google.com/?sl=en&tl=ru&text={word}&op=translate')
#ждем когда появится элемент 'Возможно вы имели в виду:  ', жмем на него
	WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME,'mvqA2c'))).click()
#ждем, когда появится перевод в правом поле, записываем результат в переменную  trans_list, конвертируем в  текст, записываем полученный перевод в переменную result, закрываем браузер
	trans_list = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'Q4iAWc')))
	result = trans_list[0].text
	driver.quit()
	return result


if __name__ == "__main__":
	with open('input_words.csv') as f:
		reader = csv.reader(f)
		for row in reader:
			if row[1] == input_word(row[0]):
				print('successfully')
			else:
				print(f'failed, result:{input_word(row[0])}, expected result:{row[1]}')

#В задании не указано, нужно ли как-то фиксировать успехи/провалы (выводить на экран или записывать в файл), в качестве отладки я использовала print. Для большого объема данных возможно будет удобней  только фэйлы выводить/записывать в файл ошибок.
#Из задания я поняла, что на входе будут только слова с неправильной раскладкой, поэтому я не учитывала случаи, когда элемент 'Возможно вы имели в виду:  ' не появляется (если вводить слово в английской раскладке)

