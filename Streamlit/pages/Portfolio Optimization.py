import streamlit as st
import numpy as np
import pandas as pd
from Portfolio_Optimization import *
import json
from datetime import date
from AFX_API import *
import plotly.express as px
from pypfopt.risk_models import sample_cov, risk_matrix
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.base_optimizer import BaseOptimizer, portfolio_performance
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage

@st.cache
def port_perf(pf, weights):

    mu = mean_historical_return(pf)
    S = CovarianceShrinkage(pf).ledoit_wolf()
    
    base_f = BaseOptimizer(len(mu), list(pf.columns))
    base_f.set_weights(weights)
    cleaned_weights = base_f.clean_weights()
    
    a, b, c = portfolio_performance(cleaned_weights, mu, S, verbose=False, risk_free_rate=0.05)
    
    return cleaned_weights, a, b, c

@st.cache
def portion_chart(port_dict: dict, optimized: bool):
    if optimized == False:
        df = {"Ticker": list(port_dict.keys()), "Weights": list(port_dict.values())}
        df_table = pd.DataFrame(df)
        fig = px.pie(df_table, names="Ticker", values="Weights", hole=0.4, title="Your Portfolio")
        return fig
    else:
        df = {"Ticker": list(port_dict.keys()), "Weights": list(port_dict.values())}
        df_table = pd.DataFrame(df)
        fig = px.pie(df_table, names="Ticker", values="Weights", hole=0.4, title="Optimized Portfolio")
        return fig

@st.cache
def amt_chart(port_dict):
    df = {"Ticker": list(port_dict.keys()), "Weights": list(port_dict.values())}
    df_table = pd.DataFrame(df)
    fig = px.pie(df_table, names="Ticker", values="Weights", title="Your Portfolio", labels=port_dict.keys())
    return fig

@st.cache
def pf_opt(df):
    mu = mean_historical_return(df)
    S = CovarianceShrinkage(df).ledoit_wolf()
    
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe(risk_free_rate=0.05)
    cleaned_weights = ef.clean_weights()
    
    a, b, c = ef.portfolio_performance(verbose=False, risk_free_rate=0.05)

    return cleaned_weights, a, b, c


def make_portfolio(portfolio_table, portfolio_data):
        cleaned_weights, a, b, c = port_perf(portfolio_table, portfolio_data)
        st.plotly_chart(portion_chart(port_dict=cleaned_weights, optimized=False), use_container_width=True)
        st.text(f"""
            Expected Annual Returns: {round(a*100, 2)}%\n
            Annual Volatility: {round(b*100, 2)}%\n
            Sharpe Ratio: {round(c, 2)}
        """)

def optimize_pf(portfolio_table):
    cleaned_weights, a, b, c = pf_opt(portfolio_table)
    st.plotly_chart(portion_chart(port_dict=cleaned_weights, optimized=True), use_container_width=True)
    st.text(f"""
        Expected Annual Returns: {round(a*100, 2)}%\n
        Annual Volatility: {round(b*100, 2)}%\n
        Sharpe Ratio: {round(c, 2)}
    """)

def backtest(port_weights):
    train = pf.loc[:str(start)]
    test = pf.loc[str(start):str(stop)]

    weights = port_weights
    stock_returns = mean_historical_return(train)
    xp_ret = 0
    for company in list(train.columns):
        xp_ret += stock_returns[company] * weights[company]

    actual_ret = (test.iloc[-1]/test.iloc[0]) - 1
    pf_perf = 0
    for company in list(train.columns):
        pf_perf += actual_ret[company] * weights[company]

    cap_app = amount * (1 + pf_perf)

    st.write(f"# Initial Capital: ₦{amount}")
    st.metric("Actual Returns",
            "₦" + str(round(cap_app - amount, 2)),
            delta=str(round(pf_perf * 100, 2)) + "%")
    st.text(f"Expected Annual Returns: {round(xp_ret * 100, 2)}%")
    

with open("Streamlit/company_data.json") as json_file:
    data = json.load(json_file)


st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="🔧",
)

tab1, tab2 = st.tabs(["Portfolio Analysis", "Backtest"])

with tab1:

    st.write("# Create a Portfolio")


    portfolio_list = st.multiselect("Choose your preferred stocks", list(data.keys()))
    port_data = {}
    for i in range(len(portfolio_list)):
        total_weight = sum(list(port_data.values())) * 100
        col1, col2 = st.columns(2)
        col1.text(f"{portfolio_list[i]}")
        weight = col2.number_input("Weight (%)", min_value=0.0, max_value=float(100 - total_weight), key=i)
        port_data[data[portfolio_list[i]]] = weight/100
        
    port_weight = sum(list(port_data.values()))

    create_button = st.button("📂 Create")

    opt_button = st.button("🛠 Optimize")

    pf = get_stocks(list(port_data.keys()), "2013-01-01", str(date.today()))

    if create_button:
        if port_weight < 1:
            st.text("Error: Total Portfolio Weight must be 100%")
        else:
            make_portfolio(pf, port_data)


    if opt_button:
        col1, col2 = st.columns(2)
        with col1:
            make_portfolio(pf, port_data)
        with col2:
            optimize_pf(pf)


with tab2:
    st.write("# Select Backtest Period")

    col1, col2, col3 = st.columns(3)
    start = col1.date_input("Enter start date", max_value=date.today())
    stop = col2.date_input("Enter stop date", min_value=start)
    amount = col3.number_input("Amount Invested (₦)")

    cl1, cl2 = st.columns(2)
    backtest_button = cl1.button("⏳ Backtest")
    opt_weight = cl2.checkbox("Use optimized portfolio weight")

    if backtest_button:
        if opt_weight:
            new_weights, a, b, c = pf_opt(pf.loc[:str(start)])
            amt_weight = {key: value * amount for key, value in new_weights.items()}
            backtest(new_weights)
            st.plotly_chart(portion_chart(amt_weight, optimized=True), use_container_width=True)

        else:
            amt_weight = {key: value * amount for key, value in port_data.items()}
            backtest(port_data)
            st.plotly_chart(amt_chart(amt_weight), use_container_width=True)
            
