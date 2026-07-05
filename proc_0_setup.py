import pandas as pd
import os
cache = r'D:\vibecoding_workspace\Codex\数据分析项目\df_cache.pkl'
if not os.path.exists(cache):
    print('Loading CSV...')
    src = r'D:\vibecoding_workspace\Codex\数据分析项目\UserBehavior_Cleaned.csv'
    dtypes = {'user_id':'int32','item_id':'int32','category_id':'int32','behavior_type':'category','timestamp':'int32'}
    df = pd.read_csv(src, header=None, names='uid iid cid btype ts'.split(), dtype=dtypes)
    df['dt'] = pd.to_datetime(df['ts'], unit='s')
    df['date'] = df['dt'].dt.date
    df['hour'] = df['dt'].dt.hour
    df['weekday'] = df['dt'].dt.dayofweek
    df['week'] = df['dt'].dt.isocalendar().week.astype(int)
    df.to_pickle(cache)
    print(f'CSV loaded, cached: {len(df):,} rows')
else:
    df = pd.read_pickle(cache)
    print(f'Loaded from cache: {len(df):,} rows')

tmin = df['dt'].min()
tmax = df['dt'].max()
print(f'Time: {tmin} ~ {tmax}')
