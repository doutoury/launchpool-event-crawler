from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from alphasurfer.crawler.launchpool.preprocessor import Preprocessor
from alphasurfer.crawler.launchpool.constant import CSSSelectors

from datetime import datetime, timedelta, timezone
import pdb


class Scraper(ABC):
    @abstractmethod
    def scrape_status():
        pass
    @abstractmethod
    def scrape_time():
        pass
    @abstractmethod
    def scrape_event():
        pass
    @abstractmethod
    def scrape_airdrop():
        pass
    @abstractmethod
    def scrape_apr():
        pass
    @abstractmethod
    def scrape_participants():
        pass


class BS4Scraper(Scraper):

    ### selector 정적메서드용 클래스랑 
    ### xpath 정적메서드용 클래스 따로 작성? 

    # for project_list
    def scrape_projects(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            project_list = source.select(selector)
        elif exchange.lower() == 'hashkey':
            project_list = source.select(selector)
        elif exchange.lower() == 'binance':
            project_list = source.select(selector)
        return project_list

    # for status_str
    def scrape_status(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            status_str = source.select(selector)[0].text
        elif exchange.lower() == 'hashkey':
            status_str = source.select(selector)[0].text
        elif exchange.lower() == 'binance':
            status_str = source.select(selector)[0].text
        return status_str

    # for time_str
    def scrape_time(self, source: BeautifulSoup, selector: str, exchange: str, status: str, selector_hours: str):
        if exchange.lower() == 'bybit':
            time_str = source.select(selector)[0].text
        elif exchange.lower() == 'hashkey': 
            time_str = source.select(selector)[0].text
        elif exchange.lower() == 'binance': 
            ### time_str 파싱 두개 필요 (time_end_str, time_delta_str) ### 
            if status == 'ON':
                delta_str = source.select(selector)[1].text
                resthours = int(source.select(selector_hours)[0].text)
                curr_dt = datetime.now(tz=timezone.utc)
                time_delta = timedelta(hours=resthours)
                day_delta = timedelta(days=1)
                end_time = curr_dt + time_delta + day_delta
                end_str = end_time.date().strftime('%Y-%m-%d')
            elif status == 'OFF':
                delta_str = source.select(selector)[1].text
                end_str = source.select(selector)[2].text
            time_str = (delta_str, end_str)
        return time_str

    # for events 
    def scrape_events(self, source: BeautifulSoup, selector: str, exchange:str):
        if exchange.lower() == 'bybit':
            event_list = source.select(selector)
        elif exchange.lower() == 'hashkey':
            event_list = source.select(selector)
        elif exchange.lower() == 'binance':
            event_list = source.select(selector)
        return event_list

    # for event_str
    def scrape_event(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            event_str = source.select(selector)[0].text
        elif exchange.lower() == 'hashkey':
            event_str = source.select(selector)[0].text
        elif exchange.lower() == 'binance':
            event_str = source.select(selector)[0].text
        return event_str

    # for total_airdrop_str
    def scrape_airdrop(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            airdrop_str = source.select(selector)[0].text
        elif exchange.lower() == 'hashkey':
            airdrop_str = source.select(selector)[0].text
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            airdrop_source = source.select(CSSSelectors().set_selectors(exchange=exchange).eventpage_airdrop_contents)[0]
            airdrop_str = airdrop_source.select(selector)[0].text
        return airdrop_str

    # for total_staking_str
    def scrape_staking(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            staking_str = source.select(selector)[0].text   # [staking, participants] 중 i=0
        elif exchange.lower() == 'hashkey':
            staking_str = source.select(selector)[1].text   # [apr, staking, participants] 중 i=1
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            staking_source = source.select(CSSSelectors().set_selectors(exchange=exchange).eventpage_stake_contents)[0]
            staking_str = staking_source.select(selector)[0].text
        return staking_str

    # for apr_str
    def scrape_apr(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            apr_str = source.select(selector)[0].text
        elif exchange.lower() == 'hashkey':
            apr_str = source.select(selector)[0].text   # [apr, staking, participants] 중 i=0
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            apr_str = ''
            # apr_str = source.select(selector)[0].text
        return apr_str

    # for total_participants_str
    def scrape_participants(self, source: BeautifulSoup, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            participants_str = source.select(selector)[1].text  # [staking, participants] 중 i=1
        elif exchange.lower() == 'hashkey':
            participants_str = source.select(selector)[2].text  # [apr, staking, participants] 중 i=2
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            participants_source = source.select(CSSSelectors().set_selectors(exchange=exchange).eventpage_stake_contents)[1]
            participants_str = participants_source.select(selector)[0].text
        return participants_str


class SeleniumScraper(Scraper):

    ### selector 정적메서드용 클래스랑 
    ### xpath 정적메서드용 클래스 따로 작성? 

    # for project_list
    def scrape_projects(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            project_list = source.find_elements(By.XPATH, selector)
        elif exchange.lower() == 'hashkey':
            project_list = source.find_elements(By.XPATH, selector)
        elif exchange.lower() == 'binance':
            project_list = source.find_elements(By.XPATH, selector)
        return project_list

    # for status_str
    def scrape_status(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            status_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'hashkey':
            status_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'binance':
            status_str = source.find_element(By.XPATH, selector).text
        return status_str

    # for time_str
    def scrape_time(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            time_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'hashkey': 
            time_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'binance': 
            ### time_str 파싱 두개 필요 (time_end_str, time_delta_str) ### 
            time_str = source.find_element(By.XPATH, selector).text
        return time_str

    # for events 
    def scrape_events(self, source: WebElement, selector: str, exchange:str):
        if exchange.lower() == 'bybit':
            event_list = source.find_elements(By.XPATH, selector)
        elif exchange.lower() == 'hashkey':
            event_list = source.find_elements(By.XPATH, selector)
        elif exchange.lower() == 'binance':
            event_list = source.find_elements(By.XPATH, selector)
        return event_list

    # for event_str
    def scrape_event(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            event_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'hashkey':
            event_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'binance':
            event_str = source.find_element(By.XPATH, selector).text
        return event_str

    # for total_airdrop_str
    def scrape_airdrop(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            airdrop_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'hashkey':
            airdrop_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            airdrop_str = source.find_element(By.XPATH, selector).text
        return airdrop_str

    # for total_staking_str
    def scrape_staking(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            staking_str = source.find_element(By.XPATH, selector).text   # [staking, participants] 중 i=0
        elif exchange.lower() == 'hashkey':
            staking_str = source.find_element(By.XPATH, selector).text   # [apr, staking, participants] 중 i=1
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            staking_str = source.find_element(By.XPATH, selector).text
        return staking_str

    # for apr_str
    def scrape_apr(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            apr_str = source.find_element(By.XPATH, selector).text
        elif exchange.lower() == 'hashkey':
            apr_str = source.find_element(By.XPATH, selector).text   # [apr, staking, participants] 중 i=0
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            apr_str = source.find_element(By.XPATH, selector).text
        return apr_str

    # for total_participants_str
    def scrape_participants(self, source: WebElement, selector: str, exchange: str):
        if exchange.lower() == 'bybit':
            participants_str = source.find_element(By.XPATH, selector).text  # [staking, participants] 중 i=1
        elif exchange.lower() == 'hashkey':
            participants_str = source.find_element(By.XPATH, selector).text  # [apr, staking, participants] 중 i=2
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            participants_str = source.find_element(By.XPATH, selector).text
        return participants_str