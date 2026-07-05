import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os, warnings
warnings.filterwarnings('ignore')

df = pd.read_pickle(r'D:\vibecoding_workspace\Codex\数据分析项目\df_cache.pkl')
out = r'D:\vibecoding_workspace\Codex\数据分析项目\charts'
os.makedirs(out, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120
colors = {'pv':'#3498db','fav':'#2ecc71','cart':'#f39c12','buy':'#e74c3c'}
labels = {'pv':'Browse','fav':'Fav','cart':'Cart','buy':'Buy'}

# 1. Daily Trend
print('[1] Daily trend...')
daily = df.groupby(['date','btype'], observed=True).size().unstack(fill_value=0)
daily.index = pd.to_datetime(list(daily.index))
fig, axes = plt.subplots(2,1,figsize=(14,10), sharex=True)
for b in ['pv','fav','cart','buy']:
    axes[0].plot(daily.index, daily[b], label=labels[b], color=colors[b], lw=1.5)
axes[0].set_title('Daily User Behavior Trend', fontsize=13)
axes[0].set_ylabel('Count'); axes[0].legend(); axes[0].grid(alpha=0.3)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
axes[1].plot(daily.index, daily['buy'], color='#e74c3c', lw=2, marker='o', markersize=3)
axes[1].set_title('Daily Purchase Trend', fontsize=13)
axes[1].set_ylabel('Count'); axes[1].grid(alpha=0.3)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
fig.autofmt_xdate(rotation=30)
plt.tight_layout(); fig.savefig(f'{out}/01_daily_trend.png', bbox_inches='tight'); plt.close()
print('  done')

# 2. Weekly
print('[2] Weekly...')
weekly = df.groupby(['week','btype'], observed=True).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,6))
x = np.arange(len(weekly)); bw = 0.2
for i,b in enumerate(['pv','fav','cart','buy']):
    ax.bar(x+i*bw, weekly[b], bw, label=labels[b], color=colors[b], alpha=0.85)
ax.set_title('Weekly Behavior Distribution', fontsize=13)
ax.set_ylabel('Count'); ax.set_xlabel('Week (2017)')
ax.set_xticks(x+bw*1.5); ax.set_xticklabels([f'W{wk}' for wk in weekly.index])
ax.legend(); ax.grid(alpha=0.3, axis='y')
plt.tight_layout(); fig.savefig(f'{out}/02_weekly_trend.png', bbox_inches='tight'); plt.close()
print('  done')

# 3. Weekday
print('[3] Weekday...')
wd_labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
wd = df.groupby(['weekday','btype'], observed=True).size().unstack(fill_value=0).reindex(range(7))
fig, axes = plt.subplots(1,2,figsize=(14,5))
for b in ['pv','fav','cart','buy']:
    axes[0].plot(wd_labels, wd[b], marker='o', label=labels[b], color=colors[b], lw=2, markersize=5)
axes[0].set_title('Behavior by Day of Week', fontsize=13)
axes[0].set_ylabel('Count'); axes[0].legend(); axes[0].grid(alpha=0.3)
wd_pct = wd.div(wd.sum(axis=1), axis=0)*100
bottom = np.zeros(7)
for b in ['pv','fav','cart','buy']:
    axes[1].bar(wd_labels, wd_pct[b], bottom=bottom, label=labels[b], color=colors[b], alpha=0.85)
    bottom += wd_pct[b]
axes[1].set_title('Behavior Share by Day (%)', fontsize=13)
axes[1].set_ylabel('Share (%)'); axes[1].legend()
plt.tight_layout(); fig.savefig(f'{out}/03_weekday_pattern.png', bbox_inches='tight'); plt.close()
print('  done')

# 4. Hourly
print('[4] Hourly...')
hourly = df.groupby(['hour','btype'], observed=True).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,6))
for b in ['pv','fav','cart','buy']:
    ax.plot(hourly.index, hourly[b], marker='o', label=labels[b], color=colors[b], lw=2, markersize=4)
ax.set_title('24-Hour User Activity Pattern', fontsize=13)
ax.set_xlabel('Hour'); ax.set_ylabel('Count')
ax.set_xticks(range(0,24))
ax.legend(); ax.grid(alpha=0.3)
peak_h = int(hourly['pv'].idxmax()); peak_v = int(hourly['pv'].max())
ax.annotate(f'Peak {peak_h}:00', xy=(peak_h,peak_v), xytext=(peak_h+1,peak_v*0.85), arrowprops=dict(arrowstyle='->'))
plt.tight_layout(); fig.savefig(f'{out}/04_hourly_pattern.png', bbox_inches='tight'); plt.close()
print('  done')

# 5. Funnel
print('[5] Funnel...')
total = {b: (df['btype']==b).sum() for b in ['pv','cart','fav','buy']}
unique = {b: df[df['btype']==b]['uid'].nunique() for b in ['pv','cart','fav','buy']}
fig, axes = plt.subplots(1,2,figsize=(14,6))
for ax, data, title in [
    (axes[0], [('Browse',total['pv']),('Cart',total['cart']),('Fav',total['fav']),('Buy',total['buy'])], 'Funnel by Events'),
    (axes[1], [('Browse',unique['pv']),('Cart',unique['cart']),('Fav',unique['fav']),('Buy',unique['buy'])], 'Funnel by Users')
]:
    mv = max(v for _,v in data)
    for i,(lbl,val) in enumerate(data):
        clr = colors[['pv','cart','fav','buy'][i]]
        ax.barh(i, val/mv, height=0.5, color=clr, alpha=0.85)
        pct = val/data[0][1]*100
        ax.text(val/mv+0.01, i, f'{val:,} ({pct:.2f}%)', va='center', fontsize=10)
    ax.set_yticks(range(4)); ax.set_yticklabels([l for l,_ in data])
    ax.invert_yaxis(); ax.set_xlim(0,1.3); ax.set_title(title, fontsize=13)
plt.tight_layout(); fig.savefig(f'{out}/05_funnel.png', bbox_inches='tight'); plt.close()
print('  done')

# 6. Top Categories
print('[6] Categories...')
cat_agg = df.groupby('cid')['btype'].value_counts().unstack(fill_value=0)
cat_agg['buy_rate'] = cat_agg['buy']/(cat_agg['pv']+1)*100
top15_pv = cat_agg.nlargest(15,'pv')
top15_rate = cat_agg[cat_agg['buy']>0].nlargest(15,'buy_rate')
fig, axes = plt.subplots(1,2,figsize=(16,6))
axes[0].barh(range(len(top15_pv)), top15_pv['pv'], color='#3498db', alpha=0.8)
axes[0].set_yticks(range(len(top15_pv))); axes[0].set_yticklabels([f'C{c}' for c in top15_pv.index])
axes[0].invert_yaxis(); axes[0].set_title('Top 15 Categories by PV', fontsize=13); axes[0].set_xlabel('PV')
axes[1].barh(range(len(top15_rate)), top15_rate['buy_rate'], color='#e74c3c', alpha=0.8)
axes[1].set_yticks(range(len(top15_rate))); axes[1].set_yticklabels([f'C{c}' for c in top15_rate.index])
axes[1].invert_yaxis(); axes[1].set_title('Top 15 by Purchase Rate', fontsize=13); axes[1].set_xlabel('Buy Rate (%)')
plt.tight_layout(); fig.savefig(f'{out}/06_top_categories.png', bbox_inches='tight'); plt.close()
print('  done')

# 7. Top Items
print('[7] Items...')
item_agg = df.groupby('iid')['btype'].value_counts().unstack(fill_value=0)
item_agg['buy_rate'] = item_agg['buy']/(item_agg['pv']+1)*100
top20_pv = item_agg.nlargest(20,'pv')
top20_buy = item_agg.nlargest(20,'buy')
fig, axes = plt.subplots(1,2,figsize=(16,7))
axes[0].barh(range(len(top20_pv)), top20_pv['pv'], color='#3498db', alpha=0.8)
axes[0].set_yticks(range(len(top20_pv))); axes[0].set_yticklabels([f'I{i}' for i in top20_pv.index])
axes[0].invert_yaxis(); axes[0].set_title('Top 20 Items by PV', fontsize=13); axes[0].set_xlabel('PV')
axes[1].barh(range(len(top20_buy)), top20_buy['buy'], color='#e74c3c', alpha=0.8)
axes[1].set_yticks(range(len(top20_buy))); axes[1].set_yticklabels([f'I{i}' for i in top20_buy.index])
axes[1].invert_yaxis(); axes[1].set_title('Top 20 Items by Purchase', fontsize=13); axes[1].set_xlabel('Buy Count')
plt.tight_layout(); fig.savefig(f'{out}/07_top_items.png', bbox_inches='tight'); plt.close()
print('  done')

# 8. Behavior Path
print('[8] Behavior path...')
user_seq = df.sort_values(['uid','ts']).groupby('uid')['btype'].agg(list).reset_index()
first_act = user_seq['btype'].apply(lambda x: x[0]).value_counts()
last_act = user_seq['btype'].apply(lambda x: x[-1]).value_counts()
bo = ['pv','cart','fav','buy']
fig, axes = plt.subplots(1,2,figsize=(14,5))
for idx,(title,dist) in enumerate([('First Behavior',first_act),('Last Behavior',last_act)]):
    vals = [dist.get(b,0) for b in bo]
    axes[idx].pie(vals, labels=None, autopct='%1.1f%%', colors=[colors[b] for b in bo], startangle=90)
    axes[idx].set_title(title, fontsize=13)
    axes[idx].legend([f'{labels[b]} ({dist.get(b,0):,})' for b in bo], loc='lower center', bbox_to_anchor=(0.5,-0.15), ncol=4)
plt.tight_layout(); fig.savefig(f'{out}/08_behavior_path.png', bbox_inches='tight'); plt.close()
print('  done')

# Summary
print()
print('='*50)
print('KEY METRICS')
print('='*50)
print(f'Users: {df["uid"].nunique():,} | Items: {df["iid"].nunique():,} | Cats: {df["cid"].nunique():,}')
print(f'Browse->Cart: {unique["cart"]/unique["pv"]*100:.2f}%')
print(f'Browse->Fav:  {unique["fav"]/unique["pv"]*100:.2f}%')
print(f'Browse->Buy:  {unique["buy"]/unique["pv"]*100:.2f}%')
print(f'Cart->Buy:    {unique["buy"]/unique["cart"]*100:.2f}%')
print(f'Fav->Buy:     {unique["buy"]/unique["fav"]*100:.2f}%')
print(f'Peak hour: {peak_h}:00')
print(f'Charts: {out}')
