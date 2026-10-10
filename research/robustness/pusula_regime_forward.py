"""Research measurement: mean 7-day forward return after each Pusula daily regime (dev period only)."""
import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from strategies.candidates.pusula import regime_score
pairs=['BTC','ETH','SOL','XRP','BNB','DOGE']
rows=[]
btc=pd.read_feather('user_data/data/binance/futures/BTC_USDT_USDT-1d-futures.feather')
btc['mkt']=regime_score(btc)
for p in pairs:
    d=pd.read_feather(f'user_data/data/binance/futures/{p}_USDT_USDT-1d-futures.feather')
    d['score']=regime_score(d)
    d=d.merge(btc[['date','mkt']],on='date')
    for h in (7,):
        d['fwd']=d['close'].shift(-h)/d['close']-1   # next 7 days from this close
    d=d[(d.date>='2020-01-01')&(d.date<'2025-01-01')].dropna(subset=['score','fwd'])
    d['pair']=p; rows.append(d)
a=pd.concat(rows); a['year']=a.date.dt.year
a['reg']=np.where(a.score>=3,'up',np.where(a.score<=-3,'down','mixed'))
print('7-day forward return % (mean), all coins, dev 2020-2024')
print((a.groupby(['year','reg'])['fwd'].mean()*100).unstack().round(2))
print((a.groupby('reg')['fwd'].agg(['mean','count'])).assign(mean=lambda x:(x['mean']*100).round(2)))
print('all days mean', round(a.fwd.mean()*100,2))
