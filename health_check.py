from bs4 import BeautifulSoup
from alphasurfer.crawler.launchpool.constant import CSSSelectors

class HealthCheck:
    # def __init__(self, exchange):
    #     self._exchange = exchange
    
    def check_launchpool(exchange):
        # Variables = CSSSelectors()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        Variables = CSSSelectors().set_selectors(exchange=exchange)

        # # 대안 1
        # project_list = Scraper.scrape_projects(source=Project, selector=Variables.project_events, exchange=self._listing.lower())
        # # or 대안 2
        # helthcheck = Scraper.health_check() # output 내용. 이 부분 raise Error 발생시키는 함수 또는 list length 리턴하는 함수 

        project_list = soup.select(Variables.projects)
        if len(project_list) == 0:
            return Exception('Web page did not open completely.') 

    def check_launchpool(url):
        
        health_check = True
        while health_check:
            self.try_connecting(url=url, max_trial=10)
            Event = BeautifulSoup(self.driver.page_source, "html.parser")
            eventpage_airdrop_selector = CSSSelectors().set_selectors(exchange=self._listing).eventpage_airdrop_contents
            eventpage_airdrop_contetns = Event.select(eventpage_airdrop_selector)
            if len(eventpage_airdrop_contetns) != 0:
                health_check = False