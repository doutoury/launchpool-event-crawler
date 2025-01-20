# Python modules 
from typing import List, Dict       # 타입선언용


# Public modules 
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from bs4.element import Tag     # 임시: 타입선언용
from selenium.webdriver.remote.webelement import WebElement     # 임시: 타입선언용

# Private modules 
from alphasurfer.crawler.launchpool.connector import BaseCrawler
from alphasurfer.crawler.launchpool.constant import LaunchpoolURL, StatusKeyword, CSSSelectors, Xpaths
from alphasurfer.crawler.launchpool.preprocessor import Preprocessor
from alphasurfer.crawler.launchpool.scraper import BS4Scraper, SeleniumScraper
from alphasurfer.crawler.launchpool.health_check import HealthCheck
from alphasurfer.crawler.launchpool.models import schema

# 테이블 초기화용 컬럼 (DB table 있는 경우, 기존 테이블 불러와서 사용하므로 불필요)
# columns = ['lock_coin', 'earn_coin', 'status', 'listing', 'start_time', 'end_time', 'total_airdrop', 'total_staking', 'apr', 'crawling_time']

# LaunchpoolCrawler 객체
class LaunchpoolCrawler(BaseCrawler):
    def __init__(self, 
                 exchange='BYBIT', 
                 browser='chrome', 
                 user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", 
                 window_size="1920x1080"):
        # 공통 브라우저 파라미터
        self._browser=browser
        self._user_agent = user_agent
        self._window_size = window_size
        # 개별 거래소 및 url 파라미터
        self._listing = exchange
        # launchpool_url = LaunchpoolURL()
        self._url = LaunchpoolURL().__dict__[exchange]
        # eventpage health check 용 멤버변수
        self._event_url = None
        # 파싱 데이터 특성값(컬럼)
        self._columns = list(schema.keys())
        self._dtypes = list(schema.values())
        # 파싱 url 접속 시간
        self.connecting_time = None

    def set_columns(self, columns: List[str]):
        self._columns = columns
    
    def scrape_events(self, Scraper, Project, Variables, status_flag):
        
        # status_flag = status

        Status = StatusKeyword().set_statuses(exchange=self._listing)
        status_check_dict = Status.get_reverse_dict()
        # Status = Status.set_statuses(exchange=self._listing)   # self._listing 속성값 사용
        # status_dict = Status.__dict__
        # status_dict_rev = dict( (value,key) for key,value in status_dict.items() )

        # status_str = Project.select(Variables.project_status)[0].text            
        status_str = Scraper.scrape_status(source=Project, selector=Variables.project_status, exchange=self._listing)
        status = status_check_dict[status_str]
        # time_str = Project.select(Variables.project_period)[0].text
        time_str = Scraper.scrape_time(source=Project, selector=Variables.project_period, exchange=self._listing, status=status, selector_hours=Variables.project_hours)
        ### Binance의 경우 ActivityCardItem_time_end와 ActivityCardItem_time_delta값 파싱 두가지 필요! ### 
        start_time = Preprocessor.preprocess_time(exchange=self._listing, time=time_str)[0]
        end_time = Preprocessor.preprocess_time(exchange=self._listing, time=time_str)[1]
        
        EventList = Scraper.scrape_events(source=Project, selector=Variables.project_events, exchange=self._listing)
        
        events_df = pd.DataFrame(columns=self._columns).astype(schema)
        for Event in EventList: 
            # event_str = Event.select(Variables.event_pair)[0].text
            event_str = Scraper.scrape_event(source=Event, selector=Variables.event_pair, exchange=self._listing)
            lock_coin = Preprocessor.preprocess_event(exchange=self._listing, event=event_str)[0]
            earn_coin = Preprocessor.preprocess_event(exchange=self._listing, event=event_str)[1]
            ### airdrop 이하부터 'binance'의 경우 개별 event 마다 
            ### 'https://launchpad.binance.com/en/launchpool/{earn_coin}_{lock_coin}' 경로 selenium 접속 후 
            ### Beutifulsoup 소스로부터 scraping 필요!
            if self._listing.lower() == 'binance':
                self._event_url = self._url + f'/launchpool/{earn_coin}_{lock_coin}'
                # SubCrawler = BaseCrawler()
                # SubCrawler.try_connecting(url=self._event_url, max_trial=10)
                # Event = BeautifulSoup(SubCrawler.driver.page_source, "html.parser")
                health_check = True
                while health_check:
                    self.try_connecting(url=self._event_url, max_trial=10)
                    Event = BeautifulSoup(self.driver.page_source, "html.parser")
                    eventpage_airdrop_selector = CSSSelectors().set_selectors(exchange=self._listing).eventpage_airdrop_contents
                    eventpage_airdrop_contetns = Event.select(eventpage_airdrop_selector)
                    if len(eventpage_airdrop_contetns) != 0:
                        health_check = False
            # total_airdrop_str = Event.select(Variables.event_airdrop)[0].text
            total_airdrop_str = Scraper.scrape_airdrop(source=Event, selector=Variables.event_airdrop, exchange=self._listing)
            total_airdrop = Preprocessor.preprocess_airdrop(exchange=self._listing, airdrop=total_airdrop_str)
            # total_staking_str = Event.select(Variables.event_stake)[0].text
            total_staking_str = Scraper.scrape_staking(source=Event, selector=Variables.event_stake, exchange=self._listing)
            total_staking = Preprocessor.preprocess_staking(exchange=self._listing, staking=total_staking_str)
            # apr_str = Event.select(Variables.event_apr)[0].text
            if self._listing.lower() != 'binence':
                apr_str = Scraper.scrape_apr(source=Event, selector=Variables.event_apr, exchange=self._listing)
                apr = Preprocessor.preprocess_apr(exchange=self._listing, apr=apr_str)
            elif self._listing.lower() == 'binence':
                apr = "Need cal."
            # apr = Preprocessor.preprocess_apr(exchange=self._listing, apr=apr_str)
            # total_participants_str = Event.select(Variables.event_participants)[1].text    # class="CardItem_totalRight__KZxrd" 중 두번째!
            total_participants_str = Scraper.scrape_participants(source=Event, selector=Variables.event_participants, exchange=self._listing)    # class="CardItem_totalRight__KZxrd" 중 두번째!
            total_participants = Preprocessor.preprocess_participants(exchange=self._listing, participants=total_participants_str)
            crawling_time = self.connecting_time

            # output
            outputs = [lock_coin, earn_coin, status, self._listing, start_time, end_time, total_airdrop, total_staking, apr, crawling_time]
            data_dict = dict(zip(self._columns, outputs))
            data_ser = pd.Series(data_dict)
            # Insert output into events_df
            events_df.loc[events_df.shape[0]] = data_ser      ##### 이 부분 series로 리턴(?)

        # return events_df if (status_flag == 'all') else events_df[events_df['status']==status_flag]
        # return events_df

        # bs4.element.Tag 객체의 .select() 메서드 결과는 class 이름 기준으로 태그를 가져오므로, 
        # 'ON'과 'OFF' status 모두에 대한 정보를 가져옴. -> 따라서 파싱 후 'ON'과 'OFF' 정보 사후선별
        if status_flag == 'all':
            return events_df
        else:
            return events_df[events_df['status']==status_flag]    # selenium 파싱 결과랑 다른 부분!
    
    def scrape_projects(self, method, status_flag):
        # 테이블 초기화 (DB table 있는 경우 불러와서 사용)
        table_df = pd.DataFrame(columns=self._columns).astype(schema)

        if method == 'class': 
            Scraper = BS4Scraper()
            Variables = CSSSelectors()
            Variables = Variables.set_selectors(exchange=self._listing)
            root_source = BeautifulSoup(self.driver.page_source, "html.parser")
            # project_list = Scraper.scrape_projects(source=root_source, selector=Variables.projects, exchange=self._listing)
            project_list = root_source.select(Variables.projects)
        
        elif method == 'xpath':
            Scraper = SeleniumScraper()
            Variables = Xpaths()
            Variables = Variables.set_xpaths(exchange=self._listing, status=status_flag)
            # project_list = Scraper.scrape_projects(source=self.driver, selector=Variables.projects, exchange=self._listing)
            project_list = self.driver.find_elements(By.XPATH, Variables.projects)

        ### Project_list 중에서 인자로 받은 status 에만 해당하는 project 에만 반복!
        Status = StatusKeyword().set_statuses(exchange=self._listing)
        status_check_dict = Status.get_reverse_dict()
        for Project in project_list: 
            status_str = Scraper.scrape_status(source=Project, selector=Variables.project_status, exchange=self._listing)
            status = status_check_dict[status_str]
            if status == status_flag:
                events_df = self.scrape_events(Scraper=Scraper, Project=Project, Variables=Variables, status_flag=status_flag)
                table_df = pd.concat([table_df, events_df], axis=0, ignore_index=True)
            else:
                continue

        # BINANCE 아니어도 selenium 통한 접속 페이지는 모두 health_check 필요할 듯? 
        # 원하는 페이지가 로드 되었는지를 해당 페이지의 핵심정보가 담긴 태그소스의 컨텐츠 유무로 확인! 
        # 아래 코드를 HealthCheck 아래 클래스 메서드 check_pagesource(url, check_selector) 생성! 
        # Binance 이면서 method='xpath' 의 경우에만 (???), 위 for 문 돌면서 scrape_events 후에 원래 페이지로 복원 필요! <- 삭제예정
        # if self._listing.lower() == 'binance':
        #     health_check = True
        #     while health_check:
        #         self.try_connecting(url=self._url, max_trial=10)
        #         RootPage = BeautifulSoup(self.driver.page_source, "html.parser")
        #         project_selector =  CSSSelectors().set_selectors(exchange=self._listing).projects
        #         project_contents = RootPage.select(project_selector)
        #         if len(project_contents) != 0:
        #             health_check = False

        print(f"Crawling {status_flag} status data was succeeded.")
        return table_df
    
    # def check_pageload(self):
    #     return HealthCheck().check_launchpool(self._listing)

    @BaseCrawler.open_webpage(max_trial=10)
    def get_launchpool_data(self, method='class', status='all'):
        if method == 'class':
            output_df = self.scrape_projects(method=method, status_flag=status)
        elif (method == 'xpath') and (status != 'all'):
            output_df = self.scrape_projects(method=method, status_flag=status)
        elif (method == 'xpath') and (status == 'all'):
            status_list = ['ON', 'SOON', 'OFF']
            # StatusKeyword().__dict__.keys()
            df_list = []
            for status_flag in status_list:
                df_list.append(self.scrape_projects(method=method, status_flag=status_flag))
                # Binance 이면서 method='xpath' 의 경우에만 (???), 위 for 문 돌면서 scrape_events 후에 원래 페이지로 복원 필요! <- 삭제예정
                if self._listing.lower() == 'binance':
                    health_check = True
                    while health_check:
                        self.try_connecting(url=self._url, max_trial=10)
                        RootPage = BeautifulSoup(self.driver.page_source, "html.parser")
                        project_selector =  CSSSelectors().set_selectors(exchange=self._listing).projects
                        project_contents = RootPage.select(project_selector)
                        if len(project_contents) != 0:
                            health_check = False
            # results = [self.scrape_projects(method=method, status_flag='ON'), 
            #            self.scrape_projects(method=method, status_flag='SOON'), 
            #            self.scrape_projects(method=method, status_flag='OFF')]
            output_df = pd.concat(df_list, axis=0, ignore_index=True)
        # 스크레이핑한 데이터들 출력 전에 타입 변경
        output_df = output_df.astype(schema)
        return output_df

        # if status == 'ON':
        #     data = self.scrape_projects(method=method, status='ON')
        # elif status == 'SOON':
        #     data = self.scrape_projects(method=method, status='SOON')
        # elif status == 'OFF':
        #     data = self.scrape_projects(method=method, status='OFF')
        # elif status == 'all':
        #     data = self.scrape_projects(method=method, status='all')
        #     # data = pd.concat([self.scrape_projects(method=method, status='ON'), self.scrape_projects(method=method, status='SOON'), self.scrape_projects(method=method, status='OFF')], axis=0, ignore_index=True)
        # else:
        #     print("Need to pass a string for 'status' argument among 'ON', 'OFF' and 'all'.")
        # return data