import streamlit as st
import sys
import os
from AFX_API import get_data
from datetime import date
import json
from YTD import predDuration

parent = os.path.abspath('.')
sys.path.insert(1, parent)

from Monte_Carlo import *


st.set_page_config(
    page_title="Monte Carlo Simulation",
    page_icon="🃏",
)

with open("Streamlit/company_data.json") as json_file:
    data = json.load(json_file)



st.write("# Monte Carlo Simulation")

defaultDate = date(date.today().year, date.today().month+1, date.today().day)

option = st.selectbox("Select Company", list(data.keys()))
col1, col2, col3 = st.columns(3)
stop = col1.date_input("Prediction Stop Date", min_value=date.today(), value=defaultDate)
no_of_preds = col2.number_input("Number of Predictions", min_value=1, step=1)
amount = col3.number_input("Amount Invested (₦)")
run = st.button("Run Simulation🎲")

tick = data[option]
df = get_data(tick, "2010-01-01", date.today())

if run:
    duration = predDuration(stop)
    forecast = monte_carlo(df, no_of_preds, duration)

    lastPrice = df["Price"].iloc[-1]
    price = round(forecast.iloc[-1].mean(), 2)
    vol = round(forecast.iloc[-1].std(), 2)
    exp_ret = (price/lastPrice)-1

    fig = px.line(forecast.iloc[-2*duration:], labels={"value": "Price", "index": "Date"})
    st.metric("Expected Return",
              "₦" + str(round(amount*exp_ret, 2)),
              delta=str(round(exp_ret*100, 2)) + "%")
    st.text(f"Projected Investment Value: ₦{round((exp_ret+1)*amount, 2)}")
    st.text(f"Current Price: ₦{lastPrice}")
    st.text(f"Expected Price: ₦{price} +/- ₦{vol}")
    st.plotly_chart(fig, use_container_width=False)
    
    



