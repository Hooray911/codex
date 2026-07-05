import pandas as pd
src = r'D:\vibecoding_workspace\Codex\数据分析项目\UserBehavior_Cleaned.csv'
dtypes = {'user_id':'int32','item_id':'int32','category_id':'int32','behavior_type':'category','timestamp':'int32'}
df = pd.read_csv(src, header=None, names=['user_id','item_id','category_id','behavior_type','timestamp'], dtype=dtypes)
df['dt'] = pd.to_datetime(df['timestamp'], unit='s')
df['date'] = df['dt'].dt.date
df['hour'] = df['dt'].dt.hour
df['weekday'] = df['dt'].dt.dayofweek
df['week'] = df['dt'].dt.isocalendar().week.astype(int)
parquet_path = r'D:\vibecoding_workspace\Codex\数据分析项目\UserBehavior_Cleaned.parquet'
df.to_parquet(parquet_path)
print(f'Parquet saved: {len(df):,} rows')
print(f'Time: {df["dt"].min()} ~ {df["dt"].max()}')
