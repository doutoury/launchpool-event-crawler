import dataclasses
from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchpoolURL:
    BYBIT: str = 'https://www.bybit.com/en/trade/spot/launchpool'
    HASHKEY: str = 'https://global.hashkey.com/en-US/launch'
    BINANCE: str = 'https://launchpad.binance.com/en'
    BITGET: str = 'https://www.bitget.com/events/launchpool'    # 보류. 

# Dataclass for status code of each exchange's launchpool web-page. 
@dataclass(frozen=True)
class StatusKeyword:
    ON: str = None
    OFF: str = None
    SOON: str = None
    
    def set_statuses(self, exchange) -> "StatusKeyword":
        # Set Bybit status code 
        if exchange.lower() == 'bybit': 
            return dataclasses.replace(self, ON='Ongoing', OFF='Ended', SOON='Coming Soon')
        # Set Hashkey status code 
        elif exchange.lower() == 'hashkey': 
            return dataclasses.replace(self, ON='Ongoing', OFF='Ended', SOON='Upcoming')
        # Set Binance status code 
        elif exchange.lower() == 'binance':
            return dataclasses.replace(self, ON='ONGOING', OFF='COMPLETED', SOON='UPCOMING')
        # Set Bitget status code 
        elif exchange.lower() == 'bitget':
            return dataclasses.replace(self, ON='Ongoing', OFF='Completed', SOON='Starting soon')
        else: 
            print("Need to pass exchange argument using set_variables() method.")

    def get_reverse_dict(self):
        return dict( (value,key) for key,value in self.__dict__.items() )

"""
ParserVariables 데이터 클래스명 변경 -> Launchpool...?
Activity 등 표현 변경 -> launchpool_project 등..? (여러개는 복수형 표현 or _children 접미사)
launchpool_encapsulated.py 에 있는 변수명도 변경
"""

@dataclass(frozen=True)
class ScraperParams:
    # Abstract xpath for Activites
    projects: str = None
    # Relative xpath for Activity (relative by each activity)
    project_status: str = None
    project_period: str = None
    # project_delta: str = None   # Only for Binance
    project_hours: str = None   # Only for Binance
    project_events: str = None
    eventpage_airdrop_contents: str = None      # Only for Binance
    eventpage_stake_contents: str = None      # Only for Binance
    # Relative xpah for result data (relative by each activity)
    event_pair: str = None
    event_airdrop: str = None
    event_stake: str = None
    event_apr: str = None
    event_participants: str = None

    def set_selectors(self, kwargs) -> "ScraperParams":
        return dataclasses.replace(self, **kwargs)

# Dataclass for xpath and class-name variables of bybit launchpool web-page. 
@dataclass(frozen=True)
class CSSSelectors(ScraperParams):
    def set_selectors(self, exchange) -> "CSSSelectors":
        if exchange.lower() == 'bybit':
            return dataclasses.replace(
                self, 
                projects='div[class^="ActivityCardItem_item_"]', 
                project_status='div[class^="ActivityCardItem_status_"]', 
                project_period='div[class^="ActivityCardItem_time_"]', 
                project_events='div[class^="CardItem_item_"]', 
                event_pair='div[class^="CardItem_dec_"]', 
                event_airdrop='div[class^="CardItem_picePoolPriceNum_"]', 
                event_stake='div[class^="CardItem_totalRight_"]', 
                event_apr='div[class^="CardItem_aprLeft_"]', 
                event_participants='div[class^="CardItem_totalRight_"]'
                )
        elif exchange.lower() == 'hashkey':
            return dataclasses.replace(
                self, 
                projects='div[class^="project-content"]', 
                project_status='p [class^="project-state"]', 
                project_period='span[class^="value mt4"]', 
                project_events='div[class^="project-join-item"]', 
                event_pair='p[class^="pool-desc"]', 
                event_airdrop='p[class^="pool-amount"]', 
                event_stake='p[class^="value flex1 text-align-right"]', 
                event_apr='p[class^="value flex1 text-align-right"]', 
                event_participants='p[class^="value flex1 text-align-right"]'
                )
        elif exchange.lower() == 'binance':
            return dataclasses.replace(
                self, 
                projects='div[name^="lp-single-project"]', 
                project_status='div[class^="css-1v046vv"]', 
                project_period ='div[class^="css-8hu9r6"]', 
                project_hours ='div[class^="css-6j58yq"]', 
                project_events='a[class^="css-1fja89h"]', 
                eventpage_airdrop_contents='div[class^="css-1m42rcb"]', 
                eventpage_stake_contents='div[class^="css-1nx27ty"]', 
                event_pair='div[class^="css-psjidm"]', 
                event_airdrop='div[class^="css-1c1ahuy"]', 
                event_stake='div[class^="css-vurnku"]', 
                event_apr='', 
                event_participants='div[class^="css-6hm6tl"]'
                )

# Dataclass for xpath and class-name variables of bybit launchpool web-page. 
@dataclass(frozen=True)
class Xpaths(ScraperParams):
    def set_xpaths(self, exchange, status) -> "Xpaths":
        if exchange.lower() == 'bybit':
            if (status == 'ON') or (status == 'SOON'):
                # 나중에 수정할 부분: projects="//*[@id='root-placeholder']/div/div[3]/div[2]/div"
                # 수정용 코드: projects="//*[@id='root-placeholder']/div/div[3]/div[contains(@class, 'NoEndActivites_content_')]/div"
                return dataclasses.replace(
                    self, 
                    projects="//*[@id='root-placeholder']/div/div[3]/div[2]/div", 
                    project_status="./div[1]", 
                    project_period="./div[2]/div[1]/div[2]/div[2]/div[2]", 
                    project_events="./div[2]/div[2]/div[contains(@class, 'CardItem_item_')]", 
                    event_pair="./div[1]/div[1]", 
                    event_airdrop="./div[1]/div[3]", 
                    event_stake="./div[1]/div[4]/div[2]/div[2]", 
                    event_apr="./div[1]/div[4]/div[1]/div[2]", 
                    event_participants="./div[1]/div[4]/div[3]/div[2]"
                    )

            elif status == 'OFF':
                # 유의: 'Ongoing' 있을 때: projects="//*[@id='root-placeholder']/div/div[3]/div[5]/div/div"
                # 유의: 'Ongoing' 없을 때: projects="//*[@id='root-placeholder']/div/div[3]/div[4]/div/div"
                return dataclasses.replace(
                    self, 
                    projects="//*[@id='root-placeholder']/div/div[3]/div[contains(@class, 'EndActivites_content_')]/div/div", 
                    project_status="./div/div[1]", 
                    project_period="./div/div[2]/div[1]/div[2]/div[1]/div[2]", 
                    project_events="./div/div[2]/div[2]/div[contains(@class, 'CardItem_item_')]", 
                    event_pair="./div[1]/div[1]/div[1]/div[2]", 
                    event_airdrop="./div[1]/div[3]", 
                    event_stake="./div[1]/div[4]/div[2]/div[2]", 
                    event_apr="./div[1]/div[4]/div[1]/div[2]", 
                    event_participants="./div[1]/div[4]/div[3]/div[2]"
                    )

        elif exchange.lower() == 'hashkey':
            pass