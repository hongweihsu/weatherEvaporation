import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
from os.path import exists


class Scraper:
    def __init__(self, url, site_list):
        self.url = url
        self.site_list = site_list
        self.header = ['Datetime', '30cm', '40cm', '50cm', '60cm', '70cm', '80cm', '90cm', '100cm']

    def fetch_moisture_percent(self):
        result = []
        site_data = {'site': '', 'datetime': '', 'percent': []}
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)

        for site in self.site_list:
            browser.get(self.url + site)
            time.sleep(5)
            # print(browser.page_source)
            soil_moisture_percent_elements = browser.find_elements(by=By.XPATH,
                                                                   value="//div[@class='traffic-light-block']//span")
            time.sleep(3)
            soil_moisture_percent = [data.text for data in soil_moisture_percent_elements]
            site_data['site'] = site
            site_data['datetime'] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            site_data['percent'] = soil_moisture_percent
            # print(site_data)
            browser.close()
            result.append(site_data.copy())

        return result

    def get_scraper_data(self):  # suppose we have sensor at 50 and 100
        site_soil_moisture_results = self.fetch_moisture_percent()  # agr vic version
        self.append_data(site_soil_moisture_results)
        cap50 = int((site_soil_moisture_results[0]['percent'][2]).replace('%', '')) * 0.3 * 0.01
        cap100 = int((site_soil_moisture_results[0]['percent'][-1]).replace('%', '')) * 0.3 * 0.01
        cap150 = None
        vic_agriculture_data = {'cap50': cap50, 'cap100': cap100, 'cap150': cap150}
        return vic_agriculture_data

    def append_data(self, site_results):
        for site_result in site_results:
            path = 'data_collection/' + site_result['site'] + '.csv'
            if not exists(path):
                with open(path, 'a+', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.header)
                    writer.writerow([site_result['datetime']] + site_result['percent'])
                    f.close()
            else:
                with open(path, 'a+', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([site_result['datetime']] + site_result['percent'])
                    f.close()

        return
