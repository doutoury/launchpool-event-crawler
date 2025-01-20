from typing import Tuple       # 타입선언용
from datetime import datetime
from datetime import timedelta


class Preprocessor:

    # for start_time, end_time
    def preprocess_time(exchange: str, time: str | Tuple):
        if exchange.lower() == 'bybit':
            start_time_str = time.split(' ~ ')[0]
            end_time_str = time.split(' ~ ')[1].split(' UTC')[0]
            # start_time, end_time 전처리
            current_year = datetime.now().year
            start_time = datetime.strptime(start_time_str, "%m-%d %H:%M")
            start_time = start_time.replace(year=current_year)
            ### output: start_time, end_time
            end_time = datetime.strptime(end_time_str, "%m-%d %H:%M")
            end_time = end_time.replace(year=current_year)
        elif exchange.lower() == 'hashkey': 
            start_time_str = time.split(' ~ ')[0]
            end_time_str = time.split(' ~ ')[1].split(' UTC')[0]
            # start_time, end_time 전처리
            current_year = datetime.now().year
            start_time = datetime.strptime(start_time_str, "%m/%d %H:%M")
            start_time = start_time.replace(year=current_year)
            ### output: start_time, end_time
            end_time = datetime.strptime(end_time_str, "%m/%d %H:%M")
            end_time = end_time.replace(year=current_year)
            end_time = end_time.replace(year=current_year)
        elif exchange.lower() == 'binance': 
            end_time = datetime.strptime(time[1], "%Y-%m-%d")
            delta_str = time[0].split(' ')[0]
            # delta_str = time[0].split(' day/s')[0]
            # delta_str = time[0].split(' lpd-balleRight-day')[0] 일 경우 발생
            start_time = end_time - timedelta(days=int(delta_str))
        return start_time, end_time

    # for lock_coin, earn_coin
    def preprocess_event(exchange: str, event: str):
        if exchange.lower() == 'bybit':
            lock_coin = event.split(' to ')[0].split('Stake ')[1]
            earn_coin = event.split(' to ')[1].split('Earn ')[1]
        elif exchange.lower() == 'hashkey':
            try:
                lock_coin = event.split(', ')[0].split('Lock ')[1]
            except:
                lock_coin = event.split(', ')[0].split('Hold ')[1]
            earn_coin = event.split(', ')[1].split('Earn ')[1]
        elif exchange.lower() == 'binance':
            lock_coin = event.split(', ')[0].split('Lock ')[1]
            earn_coin = event.split(', ')[1].split('Get ')[1].split(' Airdrop')[0]
        return lock_coin, earn_coin

    # for total_airdrop
    def preprocess_airdrop(exchange: str, airdrop: str):
        if exchange.lower() == 'bybit':
            total_airdrop = airdrop.replace(',', '_')
        elif exchange.lower() == 'hashkey':
            total_airdrop = airdrop.split(' ( ')[0]
            total_airdrop = total_airdrop.replace(',', '_')
        elif exchange.lower() == 'binance':
            total_airdrop = airdrop.split(' ')[0]
            total_airdrop = total_airdrop.replace(',', '_')
        try:
            if (total_airdrop == '--') or (total_airdrop == ''): 
                total_airdrop = '0'
            total_airdrop = float(total_airdrop)
        except:
            pass
        return total_airdrop

    # for total_staking
    def preprocess_staking(exchange: str, staking: str):
        if exchange.lower() == 'bybit':
            total_staking = staking.split(' ')[0]
            total_staking = total_staking.replace(',', '_')
        elif exchange.lower() == 'hashkey':
            total_staking = staking.split(' ')[0]
            total_staking = total_staking.replace(',', '_')
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            # total_staking = staking.split(' ')[0]
            total_staking = staking.replace(',', '_')
        try: 
            if (total_staking == '--') or (total_staking == ''): 
                total_staking = '0'
            total_staking = float(total_staking)
        except: 
            pass
        return total_staking

    # for apr
    def preprocess_apr(exchange: str, apr: str):
        if exchange.lower() == 'bybit':
            apr = apr.split('(')[0]    # selenium 파싱 결과랑 다른 부분! 이 코드 지우고, class='CardItem_noVip__8WpOH' 값만 가져와도 됨! 
            apr = apr.split('\n')[0]    # xpath 전처리 위해 이 부분 추가해도 오류 없는지 class 대상으로 확인
        elif exchange.lower() == 'hashkey':
            if ' (' in apr:
                apr = apr.split(' (')[0]
            elif ' ' in apr:
                apr = apr.split(' ')[0]
        elif exchange.lower() == 'binance':
            ### Selenium 이용해 페이지 하나 더 들어가서 정보 확인 필요 ###
            apr = '0'
            print("APR of Binance Launchpool needs to be calculated.")
        apr = apr.removesuffix('%')
        try:
            if (apr == '--') or (apr == ''): 
                apr = '0'
            apr = float(apr)
        except:
            pass
        return apr
    
    # for total_participants
    def preprocess_participants(exchange: str, participants: str):
        if exchange.lower() == 'bybit':
            total_participants = participants.replace(',', '_')
        elif exchange.lower() == 'hashkey':
            total_participants = participants.replace(',', '_')
        elif exchange.lower() == 'binance':
            total_participants = participants.replace(',', '_')
        try: 
            if (total_participants == '--') or (total_participants == ''): 
                total_participants = '0'
            total_participants = int(total_participants)
        except: 
            pass
        return total_participants