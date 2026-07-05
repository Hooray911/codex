import pandas as pd, numpy as np, matplotlib, os, warnings
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

df = pd.read_pickle(r'D:\vibecoding_workspace\Codex\数据分析项目\df_cache.pkl')
out = r'D:\vibecoding_workspace\Codex\数据分析项目\charts'
os.makedirs(out, exist_ok=True)
plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

# 1.Funnel by users
print('[1] User-level funnel...')
ub = df.groupby('uid')['btype'].apply(set).reset_index()
ub.columns = ['uid','behaviors']
n_all = len(ub)
n_pv = ub['behaviors'].apply(lambda x: 'pv' in x).sum()
n_fav = ub['behaviors'].apply(lambda x: 'fav' in x).sum()
n_cart = ub['behaviors'].apply(lambda x: 'cart' in x).sum()
n_buy = ub['behaviors'].apply(lambda x: 'buy' in x).sum()

print(f'All users: {n_all}')
print(f'Browse: {n_pv} | Browse->Fav: {n_fav/n_pv*100:.2f}%')
print(f'Fav->Cart: {n_cart/n_fav*100:.2f}% | Cart->Buy: {n_buy/n_cart*100:.2f}%')
print(f'Overall Buy: {n_buy} ({n_buy/n_pv*100:.2f}%)')
drop1 = (n_pv-n_fav)/n_pv*100
drop2 = (n_fav-n_cart)/n_fav*100
drop3 = (n_cart-n_buy)/n_cart*100
print(f'Drop-off: PV->Fav: {drop1:.1f}% | Fav->Cart: {drop2:.1f}% | Cart->Buy: {drop3:.1f}%')
max_drop = max(drop1, drop2, drop3)
max_drop_label = ['PV to Fav','Fav to Cart','Cart to Buy'][[drop1,drop2,drop3].index(max_drop)]
print(f'WORST DROP-OFF: {max_drop_label} ({max_drop:.1f}%)')

# Funnel chart
stages = ['Browse\n(PV)','Favorite\n(FAV)','Add to Cart\n(CART)','Purchase\n(BUY)']
counts = [n_pv, n_fav, n_cart, n_buy]
fig, ax = plt.subplots(figsize=(10,7))
norm = max(counts)
for i,(s,c) in enumerate(zip(stages,counts)):
    w = c/norm
    ax.barh(i, w, height=0.6, color=['#3498db','#2ecc71','#f39c12','#e74c3c'][i], alpha=0.85)
    pct = c/n_pv*100
    ax.text(w+0.01, i, f'{c:,} ({pct:.2f}%)', va='center', fontsize=11)
    if i < len(stages)-1:
        next_pct = counts[i+1]/n_pv*100
        mid = (w + counts[i+1]/norm)/2
        drop_pct = (counts[i]-counts[i+1])/counts[i]*100
        ax.annotate(f'', xy=(counts[i+1]/norm, i-0.3), xytext=(w, i-0.3),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
ax.set_yticks(range(4))
ax.set_yticklabels(stages)
ax.invert_yaxis()
ax.set_xlim(0,1.15)
ax.set_title('Complete User Conversion Funnel\n(Browse -> Favorite -> Cart -> Buy)', fontsize=14)
plt.tight_layout()
fig.savefig(f'{out}/09_funnel_detailed.png', bbox_inches='tight')
plt.close()
print('  -> 09_funnel_detailed.png')

# 2.Funnel by user activity level
print('[2] Funnel by user activity...')
user_activity = df.groupby('uid').size().reset_index(name='total_actions')
user_activity['level'] = pd.qcut(user_activity['total_actions'], q=3, labels=['Light','Medium','Heavy'])
merged = ub.merge(user_activity[['uid','level','total_actions']], on='uid')

levels = ['Light','Medium','Heavy']
fig, axes = plt.subplots(1,3,figsize=(16,5))
for idx,lvl in enumerate(levels):
    subset = merged[merged['level']==lvl]
    n_sub = len(subset)
    pv = subset['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = subset['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = subset['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = subset['behaviors'].apply(lambda x: 'buy' in x).sum()
    subs = [pv,fav,cart,buy]
    mx = max(subs)
    for i,(s,c) in enumerate(zip(['PV','FAV','CART','BUY'],subs)):
        axes[idx].barh(i,c/mx, height=0.6, color=['#3498db','#2ecc71','#f39c12','#e74c3c'][i], alpha=0.85)
        pct = c/pv*100 if pv>0 else 0
        axes[idx].text(c/mx+0.01, i, f'{c:,} ({pct:.1f}%)', va='center', fontsize=9)
    axes[idx].set_yticks(range(4))
    axes[idx].set_yticklabels(['PV','FAV','CART','BUY'])
    axes[idx].invert_yaxis()
    axes[idx].set_xlim(0,1.3)
    axes[idx].set_title(f'{lvl} Users (n={n_sub:,}, avg={subset["total_actions"].mean():.0f} actions)', fontsize=11)
axes[0].set_title(f'{levels[0]} Users (n={len(merged[merged["level"]==levels[0]]):,})', fontsize=11)
plt.tight_layout()
fig.savefig(f'{out}/10_funnel_by_activity.png', bbox_inches='tight')
plt.close()
print('  -> 10_funnel_by_activity.png')

# Print activity level details
for lvl in levels:
    subset = merged[merged['level']==lvl]
    n = len(subset)
    pv = subset['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = subset['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = subset['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = subset['behaviors'].apply(lambda x: 'buy' in x).sum()
    print(f'{lvl} ({n:,} users): PV->FAV: {fav/pv*100:.1f}% -> CART: {cart/fav*100:.1f}% -> BUY: {buy/cart*100:.1f}%')

# 3.Funnel by category (top 6 categories)
print('[3] Funnel by category...')
top_cats = df['cid'].value_counts().head(6).index.tolist()

fig, axes = plt.subplots(2,3,figsize=(16,10))
axes = axes.flatten()
for idx, cat in enumerate(top_cats):
    cdf = df[df['cid']==cat]
    cub = cdf.groupby('uid')['btype'].apply(set).reset_index()
    cub.columns = ['uid','behaviors']
    n = len(cub)
    pv = cub['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = cub['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = cub['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = cub['behaviors'].apply(lambda x: 'buy' in x).sum()
    subs = [pv,fav,cart,buy]
    mx = max(subs)
    for i,(s,c) in enumerate(zip(['PV','FAV','CART','BUY'],subs)):
        axes[idx].barh(i,c/mx, height=0.6, color=['#3498db','#2ecc71','#f39c12','#e74c3c'][i], alpha=0.85)
        pct = c/pv*100 if pv>0 else 0
        axes[idx].text(c/mx+0.01, i, f'{c:,} ({pct:.1f}%)', va='center', fontsize=9)
    axes[idx].set_yticks(range(4))
    axes[idx].set_yticklabels(['PV','FAV','CART','BUY'])
    axes[idx].invert_yaxis()
    axes[idx].set_xlim(0,1.3)
    axes[idx].set_title(f'Cat {cat} (n={n:,} users, {len(cdf):,} actions)', fontsize=10)
plt.tight_layout()
fig.savefig(f'{out}/11_funnel_by_category.png', bbox_inches='tight')
plt.close()
print('  -> 11_funnel_by_category.png')

# Print category details
for cat in top_cats:
    cdf = df[df['cid']==cat]
    cub = cdf.groupby('uid')['btype'].apply(set).reset_index()
    cub.columns = ['uid','behaviors']
    pv = cub['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = cub['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = cub['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = cub['behaviors'].apply(lambda x: 'buy' in x).sum()
    print(f'Cat {cat}: PV->FAV {fav/pv*100:.1f}% | FAV->CART {cart/fav*100:.1f}% | CART->BUY {buy/cart*100:.1f}% | Overall {buy/pv*100:.1f}%')

# 4.Funnel by hour
print('[4] Funnel by hour...')
hours = range(6,24,3)  # Sample every 3 hours
fig, axes = plt.subplots(2,3,figsize=(16,10))
axes = axes.flatten()
for idx, hr in enumerate(hours):
    hdf = df[df['hour']==hr]
    hub = hdf.groupby('uid')['btype'].apply(set).reset_index()
    hub.columns = ['uid','behaviors']
    if len(hub)==0:
        axes[idx].text(0.5,0.5,'No data', ha='center', transform=axes[idx].transAxes)
        continue
    pv = hub['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = hub['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = hub['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = hub['behaviors'].apply(lambda x: 'buy' in x).sum()
    subs = [pv,fav,cart,buy]
    mx = max(subs)
    for i,(s,c) in enumerate(zip(['PV','FAV','CART','BUY'],subs)):
        axes[idx].barh(i,c/mx, height=0.6, color=['#3498db','#2ecc71','#f39c12','#e74c3c'][i], alpha=0.85)
        pct = c/pv*100 if pv>0 else 0
        axes[idx].text(c/mx+0.01, i, f'{c:,} ({pct:.1f}%)', va='center', fontsize=9)
    axes[idx].set_yticks(range(4))
    axes[idx].set_yticklabels(['PV','FAV','CART','BUY'])
    axes[idx].invert_yaxis()
    axes[idx].set_xlim(0,1.3)
    axes[idx].set_title(f'Hour {hr}:00 (n={len(hdf):,} actions)', fontsize=11)
plt.tight_layout()
fig.savefig(f'{out}/12_funnel_by_hour.png', bbox_inches='tight')
plt.close()
print('  -> 12_funnel_by_hour.png')

# Hourly conversion rates
print()
print('Hourly conversion analysis:')
for hr in range(24):
    hdf = df[df['hour']==hr]
    hub = hdf.groupby('uid')['btype'].apply(set).reset_index()
    hub.columns = ['uid','behaviors']
    if len(hub)==0: continue
    pv = hub['behaviors'].apply(lambda x: 'pv' in x).sum()
    fav = hub['behaviors'].apply(lambda x: 'fav' in x).sum()
    cart = hub['behaviors'].apply(lambda x: 'cart' in x).sum()
    buy = hub['behaviors'].apply(lambda x: 'buy' in x).sum()
    if hr in [0,6,12,18]:
        print(f'  {hr:02d}:00 - PV->FAV: {fav/pv*100:.1f}% | FAV->CART: {cart/fav*100:.1f}% | CART->BUY: {buy/cart*100:.1f}% | Overall: {buy/pv*100:.1f}%')

# 5.Summary stats
print()
print('='*60)
print('FUNNEL ANALYSIS SUMMARY')
print('='*60)
print(f'Total unique users: {n_all:,}')
print(f'Funnel: Browse({n_pv:,}) -> Fav({n_fav:,}) -> Cart({n_cart:,}) -> Buy({n_buy:,})')
print(f'Stage 1-2 (PV->FAV) drop-off: {drop1:.1f}% ({n_pv-n_fav:,} users lost)')
print(f'Stage 2-3 (FAV->CART) drop-off: {drop2:.1f}% ({n_fav-n_cart:,} users lost)')
print(f'Stage 3-4 (CART->BUY) drop-off: {drop3:.1f}% ({n_cart-n_buy:,} users lost)')
print(f'WORST DROP-OFF POINT: {max_drop_label} ({max_drop:.1f}% loss)')
print()
print(f'Overall browse-to-buy conversion: {n_buy/n_pv*100:.2f}%')
print(f'Users who did all 4 behaviors: {n_all_four:,} ({n_all_four/n_all*100:.2f}%)')
print(f'Charts saved to: {out}')
