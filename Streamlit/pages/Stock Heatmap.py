import streamlit as st
import numpy as np
import pandas as pd
from Portfolio_Optimization import *
import json
from datetime import date
import requests
import re
from AFX_API import *
import plotly.express as px

st.set_page_config(
    page_title="NSE Stock Heatmap",
    page_icon="🔥",
)

st.write("# Market Returns Heatmap")

pf = pd.read_csv("Streamlit/pages/stock_heatmap.csv")

returns = pf["YTD Return"].tolist()
market_cap = pf["Market Cap"].tolist()

fig = px.treemap(pf, path=[px.Constant("All Share Index"), "Sector", "Ticker"],
                 values = "Market Cap", color = "YTD Return",
                 hover_data = {"YTD Return":":.2p", "Market Cap": ":.2f"}, color_continuous_scale='RdYlGn',
                 color_continuous_midpoint=0, 
                 range_color = [-0.5, 0.5],
                 width=900,
                 height=500)

fig.data[0].customdata = np.column_stack([returns, market_cap])
fig.data[0].texttemplate = "%{label}<br>Market Cap:₦%{value}B<br>YTD Return:%{customdata[0]:.2p}"

fig.update_layout(margin = dict(l=5, r=5, t=20, b=5))

st.plotly_chart(fig, use_container_width=False)
