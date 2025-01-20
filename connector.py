import time
import signal
import random
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from alphasurfer.crawler.launchpool.health_check import HealthCheck
from alphasurfer.crawler.launchpool.constant import CSSSelectors

# Crawler base 객체 
class BaseCrawler():
    def __init__(self, 
                 browser='chrome', 
                 user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", 
                 window_size="1920x1080"):
        # 브라우저 파라미터 (공통 적용되는 것들만!)
        # self._driver = None
        self._browser=browser
        self._user_agent = user_agent
        self._window_size = window_size

    def set_options(self, browser, user_agent, window_size):
        self._browser=browser
        self._user_agent = user_agent
        self._window_size = window_size

    def connect_webdriver(self):
        if self._browser == 'chrome':
            self.options = webdriver.ChromeOptions()
            self.options.add_argument(self._user_agent)        # chrome 화면 접속 user-agent
            self.options.add_argument(self._window_size)       # chrome 화면 사이즈
            self.options.add_argument('--no-sandbox')         # root 계정 허용
            self.options.add_argument('--incognito')          # 시크릿 모드
            # self.options.add_argument('--remote-debugging-port=9222')   # http://localhost:9222 로 디버깅
            self.options.add_argument('--disable-blink-features=AutomationControlled')        # 자동화 탐지 방지 
            self.options.add_experimental_option('excludeSwitches', ['enable-automation'])    # 자동화 표시 제거
            self.options.add_experimental_option('useAutomationExtension', False)      
            self.driver = webdriver.Chrome(options=self.options)   # 드라이버 초기화
        elif self._browser == 'firefox':
            self.options = webdriver.FirefoxOptions()
            # Need to Fix
        elif self._browser == 'edge': 
            self.options = webdriver.EdgeOptions()
            # Need to Fix
        elif self._browser == 'safari':
            self.options = webdriver.SafariOptions()
            # Need to Fix
        else:
            print("Pass a browser name into 'browser' argument.")
        # 셀레니움이 컨트롤하는 크롬 인스턴스의 navigator.webdriver 플래그를 변경하는 javascript 실행 
        # self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def disconnect_webdriver(self):
        self.driver.quit()

    def try_connecting(self, url, max_trial):
        num_trial = 1
        while num_trial != max_trial:
            try:
                self.connect_webdriver()
                time.sleep(0.5)
                self.driver.get(url)
                time.sleep(1)    # driver.get(url) 결과 페이지 로딩 안 기다리면, 페이지 로딩 확인 전에 break 으로 다음과정 진입해서 데이터 0개 반환되는 경우 발생.
                break
            except:
                if self.driver.service.process.poll(): self.disconnect_webdriver()
                print(f"{num_trial}'th trial getting to '{url}' was failed.")
            num_trial += 1
            time.sleep(random.uniform(2, 4))    # 2~4 초 사이 시간으로 코드슬립
        self.connecting_time = datetime.now()

    # 폐기예정: 이유 -> selector 변수에 들어가는 Variables 값들이 다 다름... (파싱해야하는 리스트 대상이 다르기 때문에)
    def check_pageload(timeout):
        def decorator(func):
            def wrapper(self, *args, **kargs):
                start = time.time()
                pageload_state = 'incomplete'
                while (pageload_state == 'incomplete') and (time.time() < start + timeout) :
                    # self.try_connecting(url=url, max_trial=10)
                    func(*args, **kargs)
                    Event = BeautifulSoup(self.driver.page_source, "html.parser")
                    eventpage_airdrop_selector = CSSSelectors().set_selectors(exchange=self._listing).eventpage_airdrop_contents
                    eventpage_airdrop_contetns = Event.select(eventpage_airdrop_selector)
                    if len(eventpage_airdrop_contetns) != 0:
                        pageload_state = 'complete'
            return wrapper
        return decorator

    # open_launchpoolpage 로 이름 변경
    def open_webpage(max_trial):
        def decorator(func):
            def wrapper(self, *args, **kargs):
                health_check = True
                while health_check:
                    # tru_connecting() 결과 비정상 페이지 로드된 경우 health_check
                    self.try_connecting(url=self._url, max_trial=max_trial)
                    RootPage = BeautifulSoup(self.driver.page_source, "html.parser")
                    project_selector =  CSSSelectors().set_selectors(exchange=self._listing).projects
                    project_contents = RootPage.select(project_selector)
                    if len(project_contents) != 0:
                        health_check = False
                    else: 
                        self.disconnect_webdriver()
                print("Getting page is done.")

                result = func(self, *args, **kargs)
                print("Crawling job is done.")

                self.disconnect_webdriver()
                print("Browser-driver is closed.")
                
                return result
            return wrapper
        return decorator