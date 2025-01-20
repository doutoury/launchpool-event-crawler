from numpy import datetime64

# ['lock_coin', 'earn_coin', 'status', 'listing', 'start_time', 'end_time', 'total_airdrop', 'total_staking', 'apr', 'crawling_time']
# ['string', 'string', 'string', 'string', 'datetime64[ns]', 'datetime64', 'Float64', 'Float64', 'Float64', 'datetime64']
schema = {'lock_coin': str, 
          'earn_coin': str, 
          'status': str, 
          'listing': str, 
          'start_time': 'datetime64[ns]', 
          'end_time': 'datetime64[ns]', 
          'total_airdrop': float, 
          'total_staking': float, 
          'apr': float, 
          'crawling_time': 'datetime64[ns]'
          }