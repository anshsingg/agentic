import streamlit as st
import math,random
import matplotlib.pyplot as plt

st.title('Smart EV Charging Route — DP TSP (Bitmask)')
st.markdown('Upload CSV of charging stations (x,y)')

def dist(a,b):
    return math.hypot(a[0]-b[0],a[1]-b[1])

uploaded = st.file_uploader('CSV: x,y (no header)', type=['csv'])
if uploaded:
    data = [tuple(map(float,line.strip().split(','))) for line in uploaded.getvalue().decode().strip().splitlines()]

    m = len(data)
    d = [[dist(data[i],data[j]) for j in range(m)] for i in range(m)]

    INF = 10**9
    N = m
    ALL = 1<<N
    dp = [[INF]*N for _ in range(ALL)]
    parent = [[-1]*N for _ in range(ALL)]
    dp[1][0]=0

    for mask in range(ALL):
        for u in range(N):
            if not (mask & (1<<u)): continue
            cur = dp[mask][u]
            if cur>=INF: continue
            for v in range(N):
                if mask & (1<<v): continue
                nm = mask | (1<<v)
                nd = cur + d[u][v]
                if nd < dp[nm][v]:
                    dp[nm][v] = nd
                    parent[nm][v] = u

    best = INF; last = -1; full = ALL-1
    for i in range(N):
        val = dp[full][i] + d[i][0]
        if val < best:
            best = val; last = i

    route = []
    mask = full
    while last!=-1:
        route.append(last)
        p = parent[mask][last]
        mask ^= (1<<last)
        last = p
    route = list(reversed(route))
    route.append(0)

    st.metric('Total energy (distance)', round(best,3))
    xs = [data[i][0] for i in route]
    ys = [data[i][1] for i in route]

    fig,ax = plt.subplots()
    ax.plot(xs,ys,'-o')
    for i,(x,y) in enumerate(data):
        ax.text(x,y,f'{i}',fontsize=9,ha='right')
    ax.set_title('Route (indices shown)')
    st.pyplot(fig)

    st.write('Visit order (indices):', route)
    st.write('Coordinates list:', data)
