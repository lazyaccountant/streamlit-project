import streamlit as st
from Portfolio_Optimization import *
import json
from datetime import date
from AFX_API import *
import plotly.express as px
from YTD import daysCount

st.set_page_config(
    page_title="Market Overview",
    page_icon="📈",
)

with open("Streamlit/company_data.json") as json_file:
    data = json.load(json_file)

daysCount = daysCount()


period_dict = {"1M": 21, "3M": 63, "6M": 126, "1Y": 252, "YTD": daysCount, "MAX": 0}


option = st.selectbox("Enter Company Name", list(data.keys()))
period = st.sidebar.selectbox("Period", list(period_dict.keys()))
comp = st.sidebar.selectbox("Compare with...", [""]+list(data.keys()))

dataframe = get_data(data[option], "2010-01-01", str(date.today()))
returns = dataframe.pct_change().dropna(how="all")

def defaultchart(company_name, df, period, duration):
    lastPrice = df["Price"].iloc[-1]
    previousDayPrice = df["Price"].iloc[-2]
    previousPrice = df["Price"].iloc[-1*period]
    period_ret = (lastPrice / previousPrice) - 1
    st.write(f"""
        # {company_name}""")
    col1, col2, col3 = st.columns(3)
    col1.write(f"""# ₦{df["Price"].iloc[-1]}
        """)
    col2.metric("1D Return",
                "₦" + str(round(lastPrice-previousDayPrice, 2)),
                delta=str(round(returns["Price"].iloc[-1] * 100, 2)) + "%")
    col3.metric(f"{duration} Return",
                "₦" + str(round(lastPrice-previousPrice, 2)),
                delta=str(round(period_ret*100, 2)) + "%")
    fig = px.line(df.iloc[-1*period:], labels={"value": "Price (₦)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def comparechart(company_name, comp_name, df, period): 
    col1, col2 = st.columns(2)
    col1.write(f"""
        # {company_name}""")
    col1.write(f"""# ₦{df[df.columns[0]].iloc[-1]}
        """)

    col2.write(f"""
        # {comp_name}""")
    col2.write(f"""# ₦{df[df.columns[1]].iloc[-1]}
        """)

    pf = df.iloc[-1*period:]
    pf = (pf/pf.iloc[0] - 1) * 100

    fig = px.line(pf, labels={"value": "Returns (%)"})
    fig.update_layout(legend=dict(title=None, yanchor="top", y=0.99, xanchor="left", x=0.01))

    st.plotly_chart(fig, use_container_width=True)
    #st.line_chart(pf, x="Date", y="Returns (%)")


if comp == "":
    defaultchart(company_name=option, df=dataframe, period=period_dict[period], duration=period)

else:
    pair = [data[option], data[comp]]
    data_load_state = st.text('Loading data...')
    pair_data = get_stocks(pair, "2010-01-01", str(date.today()))
    data_load_state.text('')
    comparechart(option, comp, pair_data, period_dict[period])
