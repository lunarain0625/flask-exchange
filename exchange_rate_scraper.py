import sys
import logging
import configparser
from pathlib import Path
import threading
import os
import csv
from datetime import datetime
import json

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def process_cba(driver, source):
    try:
        driver.get('https://www.commbank.com.au/international/foreign-exchange-rates.html')
    except:
        logging.error(f'Failed to acceess source {source}, skip this source')
        driver.quit()
        return
    capture_time = datetime.now()
    capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')

    symbol_list = ['JPY', 'USD', 'CNY', 'SGD', 'HKD', 'EUR', 'GBP']

    for symbol in symbol_list:
        try:
            buy_rate = driver.find_element(
                By.XPATH, 
                f'//div[@data-category="{symbol}"]//span[text()="Send IMT"]/following-sibling::div[1]'
            ).get_attribute('innerText')
            logging.info(f'Captured {symbol}_buy: {buy_rate}')
            row_list.append([capture_time, source, f'{symbol}_buy', format_numeric_string(buy_rate)])

            sell_rate = driver.find_element(
                By.XPATH,
                f'//div[@data-category="{symbol}"]//span[text()="Receive IMT"]/following-sibling::div[1]'
            ).get_attribute('innerText')
            logging.info(f'Captured {symbol}_sell: {sell_rate}')
            row_list.append([capture_time, source, f'{symbol}_sell', format_numeric_string(sell_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()
        

def process_anz(driver, source):
    try:
        driver.get('https://www.anz.com.au/personal/travel-international/foreign-exchange-rates/')
    except:
        logging.error(f'Failed to acceess source {source}, skip this source')
        driver.quit()
        return
    capture_time = datetime.now()
    capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')

    symbol_list = ['JPY', 'USD', 'CNY', 'SGD', 'HKD', 'EUR', 'GBP']
    for symbol in symbol_list:
        try:
            buy_rate = driver.find_element(
                By.XPATH,
                f'//div[@aria-labelledby="tab-1"]//td[@data-code="{symbol}"]/following-sibling::td[1]'
            ).get_attribute('innerText')
            logging.info(f'Captured {symbol}_buy: {buy_rate}')
            row_list.append([capture_time, source, f'{symbol}_buy', format_numeric_string(buy_rate)])

            sell_rate = driver.find_element(
                By.XPATH,
                f'//div[@aria-labelledby="tab-2"]//td[@data-code="{symbol}"]/following-sibling::td[1]'
            ).get_attribute('innerText')
            logging.info(f'Captured {symbol}_sell: {sell_rate}')
            row_list.append([capture_time, source, f'{symbol}_sell', format_numeric_string(sell_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def process_wise(driver, source):
    symbol_list = ['JPY', 'USD', 'CNY', 'SGD', 'HKD', 'EUR', 'GBP']
    for symbol in symbol_list:
        try:
            driver.get(f'https://wise.com/au/compare/western-union-aud-to-{symbol}')
            capture_time = datetime.now()
            capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')
            midmarket_rate = driver.find_element(
                By.XPATH,
                '//strong[@id="route-rate"]'
            ).get_attribute('innerText').replace('1 AUD = ','').replace(f' {symbol}','')
            logging.info(f'Captured AUD_to_{symbol}_midmarket: {midmarket_rate}')
            row_list.append([capture_time, source, f'AUD_to_{symbol}_midmarket', format_numeric_string(midmarket_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def process_webtradepay(driver, source):
    try:
        driver.get('https://r.superforex.com.au/rates_cron.json')
    except:
        logging.error(f'Failed to acceess source {source}, skip this source')
        driver.quit()
        return
    capture_time = datetime.now()
    capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')
    json_text = driver.find_element(By.TAG_NAME, "pre").get_attribute('innerText')
    price_dict = json.loads(json_text)

    symbol_list = ['JPY', 'USD', 'RMB', 'SGD', 'HKD', 'EUR', 'GBP']
    for symbol in symbol_list:
        try:
            buy_rate = price_dict[f'AUD{symbol}']['kbuy']
            sell_rate = price_dict[f'AUD{symbol}']['ksell']
            if symbol == 'RMB':
                symbol = 'CNY'
            logging.info(f'Captured {symbol}_buy: {buy_rate}')
            logging.info(f'Captured {symbol}_sell: {sell_rate}')
            row_list.append([capture_time, source, f'{symbol}_buy', format_numeric_string(buy_rate)])
            row_list.append([capture_time, source, f'{symbol}_sell', format_numeric_string(sell_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def process_pandaremit(driver, source):
    symbol_list = ['JPY', 'USD', 'CNY', 'SGD', 'HKD', 'EUR', 'GBP']
    for symbol in symbol_list:
        try:
            # CNY needs special process
            if symbol == 'CNY':
                driver.get('https://www.pandaremit.com/en/aus/china/aud-cny-converter')
                capture_time = datetime.now()
                capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')
                midmarket_rate = driver.find_element(
                    By.XPATH,
                    '//tbody/tr[2]/td[2]'
                ).get_attribute('innerHTML')
            else:
                driver.get(f'https://prod.pandaremit.com/pricing/rate/AUD/{symbol}')
                capture_time = datetime.now()
                capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')
                json_text = driver.find_element(By.TAG_NAME, "pre").get_attribute('innerText')
                price_dict = json.loads(json_text)
                midmarket_rate = price_dict['model']['huiOut']
            logging.info(f'Captured AUD_to_{symbol}_midmarket: {midmarket_rate}')
            row_list.append([capture_time, source, f'AUD_to_{symbol}_midmarket', format_numeric_string(midmarket_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def process_moneychase(driver, source):
    try:
        driver.get('https://www.moneychase.com.au/')
        # Need to explicitly wait for a separate request to be finished to get all the 
        # rates, without this explicit wait the result could be empty sometimes
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((
                    By.XPATH, 
                    f'//div[@id="rateQuoteDIV"]//tr[td[contains(text(),"澳元/人民币") and img[contains(@src,"australia.png")]]]/td[@data-th="Ask"]'
                ), '')
        )
    except:
        logging.error(f'Failed to acceess source {source}, skip this source')
        driver.quit()
        return
    capture_time = datetime.now()
    capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')

    symbol_list = [
        {
            'english':'JPY', 'chinese':'澳元/日元'
        }, 
        {
            'english':'USD', 'chinese':'澳元/美元'
        },
        {
            'english':'CNY', 'chinese':'澳元/人民币'
        },
        {
            'english':'SGD', 'chinese':'澳元/新加坡元'
        },
        {
            'english':'HKD', 'chinese':'澳元/港币'
        },
        {
            'english':'EUR', 'chinese':'澳元/欧元'
        },
        {
            'english':'GBP', 'chinese':'澳元/英镑'
        }
    ]
    for symbol in symbol_list:
        english = symbol['english']
        chinese = symbol['chinese']
        try:
            # 澳元/人民币 needs to be processed separately as there are 
            # 2 澳元/人民币 values, we need to choose the value for normal one, 
            # instead of the VIP one
            if english == 'CNY':
                buy_rate = driver.find_element(
                    By.XPATH,
                    f'//div[@id="rateQuoteDIV"]//tr[td[contains(text(),"{chinese}") and img[contains(@src,"australia.png")]]]/td[@data-th="Ask"]'
                ).get_attribute('innerText')

                sell_rate = driver.find_element(
                    By.XPATH, 
                    f'//div[@id="rateQuoteDIV"]//tr[td[contains(text(),"{chinese}") and img[contains(@src,"australia.png")]]]/td[@data-th="BID"]'
                ).get_attribute('innerText')
            else:
                buy_rate = driver.find_element(
                    By.XPATH,
                    f'//div[@id="rateQuoteDIV"]//tr[td[contains(text(),"{chinese}")]]/td[@data-th="Ask"]'
                ).get_attribute('innerText')

                sell_rate = driver.find_element(
                    By.XPATH,
                    f'//div[@id="rateQuoteDIV"]//tr[td[contains(text(),"{chinese}")]]/td[@data-th="BID"]'
                ).get_attribute('innerText')
            logging.info(f'Captured {english}_buy: {buy_rate}')
            row_list.append([capture_time, source, f'{english}_buy', format_numeric_string(buy_rate)])
            logging.info(f'Captured {english}_sell: {sell_rate}')
            row_list.append([capture_time, source, f'{english}_sell', format_numeric_string(sell_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def process_moneychain(driver, source):
    try:
        driver.get('https://www.moneychain.com.au/')
    except:
        logging.error(f'Failed to acceess source {source}, skip this source')
        driver.quit()
        return
    capture_time = datetime.now()
    capture_time = capture_time.strftime('%Y-%m-%d %H:%M:%S')
    
    symbol_list = [
        {
            'english':'JPY', 'chinese':'澳元/日币'
        }, 
        {
            'english':'USD', 'chinese':'澳元/美金'
        },
        {
            'english':'CNY', 'chinese':'澳元/人民币'
        },
        {
            'english':'SGD', 'chinese':'澳元/新币'
        },
        {
            'english':'HKD', 'chinese':'澳元/港币'
        },
        {
            'english':'EUR', 'chinese':'澳元/欧元'
        },
        {
            'english':'GBP', 'chinese':'澳元/英镑'
        }
    ]
    for symbol in symbol_list:
        english = symbol['english']
        chinese = symbol['chinese']
        try:
            buy_rate = driver.find_element(
                By.XPATH,
                f'//div[h3/strong[contains(text(), "实时汇率")]]/following-sibling::div//td[contains(text(), "{chinese}")]/following-sibling::td[1]'
            ).get_attribute('innerText')
            logging.info(f'Captured {english}_buy: {buy_rate}')
            row_list.append([capture_time, source, f'{english}_buy', format_numeric_string(buy_rate)])

            sell_rate = driver.find_element(
                By.XPATH,
                f'//div[h3/strong[contains(text(), "实时汇率")]]/following-sibling::div//td[contains(text(), "{chinese}")]/following-sibling::td[2]'
            ).get_attribute('innerText')
            logging.info(f'Captured {english}_sell: {sell_rate}')
            row_list.append([capture_time, source, f'{english}_sell', format_numeric_string(sell_rate)])
        except:
            logging.error(f'Failed to access symbol {symbol} in source {source}, skip this symbol')
            continue
    driver.quit()


def save_price():
    logging.info('Started writing result to csv')
    with open(csv_file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in row_list:
            csv_writer.writerow(row)
    logging.info('Finished writing result to csv')


def create_driver():
    while True:
        try:
            chrome_options = Options()
            # chrome_options.binary_location = config['GENERAL']['CHROME_BINARY_LOCATION']
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            chrome_options.add_argument('--headless')

            chrome_options.add_argument('--no-sandbox')
            service = Service(executable_path=config['GENERAL']['CHROMEDRIVER_EXECUTABLE_PATH'])
            driver = Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            break
        except Exception as err:
            logging.error(
                'Exception happened during creating driver, '
                f'error: {err}. Retry now'
            )
            continue
    return driver


def request_thread(source):
    logging.info(f'Started scraping {source}')
    driver = create_driver()
    switch_dict = {
        'cba': process_cba,
        'anz': process_anz,
        'wise': process_wise,
        'webtradepay': process_webtradepay,
        'pandaremit': process_pandaremit,
        'moneychase': process_moneychase,
        'moneychain': process_moneychain,
    }
    switch_dict[source](driver=driver, source=source)


def create_file_if_not_exist(file_path):
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: '{directory}'")

        # Create the file
        with open(file_path, 'w') as file:
            file.write('capture_time,source,item,value\n')
            logging.info(f"Created file: '{file_path}'")


def format_numeric_string(numeric_string):
    numeric_string = numeric_string.strip()
    if numeric_string.replace(".", "").isnumeric():
        return '{:.8f}'.format(float(numeric_string))
    else:
        return ''


def main():
    source_list = config['GENERAL']['SOURCE_LIST'].split()
    thread_list = []
    for source in source_list:
        rt = threading.Thread(
            target=request_thread, name=f'{source}Thread', args=(source,)
        )
        thread_list.append(rt)
        rt.start()

    for thread in thread_list:
        thread.join()

    save_price()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config_file_path = Path(__file__).with_name('config.ini')
    config.read(config_file_path)
    sys.stdout = open(config['GENERAL']['STDOUT_FILE_PATH'], 'w')
    sys.stderr = open(config['GENERAL']['STDERR_FILE_PATH'], 'w')
    logging.basicConfig(
        filename=config['GENERAL']['LOG_FILE_PATH'],
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
        level=logging.INFO
    )
    logging.info("==========================")
    logging.info("Program start - Exchange Rate Scraper")
    logging.info("==========================")
    row_list = []
    csv_file_path = config['GENERAL']['CSV_FILE_PATH']
    create_file_if_not_exist(csv_file_path)
    main()
    logging.info("==========================")
    logging.info("Program end - Exchange Rate Scraper")
    logging.info("==========================")