import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import os
out_dir = r"D:\vibecoding_workspace\Codex\数据分析项目\charts"
os.makedirs(out_dir, exist_ok=True)
plt.rcParams["font.sans-serif"] = ["SimHei","Microsoft YaHei","DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 120
print("Loading data...")
src = r"D:\vibecoding_workspace\Codex\数据分析项目\UserBehavior_Cleaned.csv"
dtypes = {"user_id":"int32","item_id":"int32","category_id":"int32","behavior_type":"category","timestamp":"int32"}
df = pd.read_csv(src, header=None, names=["user_id","item_id","category_id","behavior_type","timestamp"], dtype=dtypes)
print(f"Loaded: {len(df):,} rows")
df["dt"] = pd.to_datetime(df["timestamp"], unit="s")
df["date"] = df["dt"].dt.date
df["hour"] = df["dt"].dt.hour
df["weekday"] = df["dt"].dt.dayofweek
df["week"] = df["dt"].dt.isocalendar().week.astype(int)
print(f'Time: {df["dt"].min()} ~ {df["dt"].max()}')
colors = {"pv":"#3498db","fav":"#2ecc71","cart":"#f39c12","buy":"#e74c3c"}
labels = {"pv":"Browse","fav":"Fav","cart":"Cart","buy":"Buy"}
