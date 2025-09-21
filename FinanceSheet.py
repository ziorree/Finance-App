import streamlit as st

st.title('Financial Manager')


st.sidebar.header('Menu')
menu = st.sidebar.selectbox('Select an option:', ['Dashboard', 'Add Item', 'View Items', 'Analytics'])

import pandas as pd

import numpy as np
import datetime
import yfinance as yf


if menu == 'Dashboard':
    st.write('Welcome to your financial dashboard!')
elif menu == 'Add Item':
    st.write('Add a new financial item here.')
elif menu == 'View Items':
    st.write('Here are your financial items.')
elif menu == 'Analytics':
    st.header('Analytics & Forecasting')
    st.write('Forecast your net worth and account balances for 10, 20, and 30 years by month, including dividends and debt paydown.')
    st.info('This page will use your current monthly plan, debt schedules, and investment allocations to project your net worth. You can customize the next 12 months, and future years will use the last month as a baseline.')
    # Placeholder for future: custom 12-month input table
    st.subheader('12-Month Forward Inputs (Coming Soon)')
    # Placeholder for future: debt schedule integration
    st.subheader('Debt Schedules (Coming Soon)')
    # Placeholder for future: forecast chart
    st.subheader('Net Worth Forecast (Coming Soon)')
    st.write('Forecast logic and charts will be implemented here.')

# --- Monthly Income and Bills/Contributions Section ---
st.header('Monthly Income and Payments')


# --- Editable Monthly Plan Table ---
st.subheader('Monthly Plan')

# Month selector
month_options = [
    (datetime.date.today() + datetime.timedelta(days=30*i)).strftime('%B %Y')
    for i in range(0, 12)
]
selected_month = st.selectbox('Select month:', month_options, index=0)

# Default plan data (can be loaded from file/db in future)
default_plan = [
    {'Name': 'Net Pay', 'Amount': 4400, 'Account': '', 'Asset': '', 'Paid': False},
    {'Name': 'Car Insurance/Gym', 'Amount': -512, 'Account': '', 'Asset': '', 'Paid': False},
    {'Name': 'Brokerage Main', 'Amount': -250, 'Account': 'Main Brokerage', 'Asset': 'SPRX', 'Paid': False},
    {'Name': 'BTC', 'Amount': -250, 'Account': 'BTC', 'Asset': 'BTC', 'Paid': False},
    {'Name': 'Savings', 'Amount': -1000, 'Account': 'Savings', 'Asset': '', 'Paid': False},
    {'Name': 'Food', 'Amount': -700, 'Account': '', 'Asset': '', 'Paid': False},
    {'Name': 'Loan', 'Amount': -500, 'Account': 'Shared', 'Asset': 'QQQI', 'Paid': False},
    {'Name': 'Gas cost', 'Amount': -150, 'Account': '', 'Asset': '', 'Paid': False},
    {'Name': 'Car Payment', 'Amount': -1000, 'Account': 'Shared', 'Asset': 'Money Fund', 'Paid': False},
    {'Name': 'Travel', 'Amount': 0, 'Account': '', 'Asset': '', 'Paid': False},
]

plan_df = st.data_editor(
    default_plan,
    column_config={
        'Name': st.column_config.TextColumn('Name'),
        'Amount': st.column_config.NumberColumn('Amount', format='$%.2f'),
        'Account': st.column_config.TextColumn('Account'),
        'Asset': st.column_config.TextColumn('Asset'),
        'Paid': st.column_config.CheckboxColumn('Paid'),
    },
    num_rows='dynamic',
    key=f'plan_{selected_month}'
)

# Calculate totals and allocations
total_income = sum(row['Amount'] for row in plan_df if row['Amount'] > 0)
total_out = sum(row['Amount'] for row in plan_df if row['Amount'] < 0)
st.write(f"**Total Income:** ${total_income:,.2f}")
st.write(f"**Total Outflows:** ${-total_out:,.2f}")
st.write(f"**Net for Month:** ${total_income + total_out:,.2f}")

# Show allocations by account and asset
st.subheader('Account Allocations')
alloc_df = {}
for row in plan_df:
    acct = row['Account'] or 'Unassigned'
    alloc_df.setdefault(acct, 0)
    alloc_df[acct] += row['Amount']
st.write(alloc_df)

st.subheader('Asset Allocations')
asset_df = {}
for row in plan_df:
    asset = row['Asset'] or 'Unassigned'
    asset_df.setdefault(asset, 0)
    asset_df[asset] += row['Amount']
st.write(asset_df)

# Example: Fetch live price for SPRX using yfinance
if 'SPRX' in asset_df and asset_df['SPRX'] != 0:
    try:
        sprx = yf.Ticker('SPRX')
        sprx_price = sprx.history(period='1d')['Close'].iloc[-1]
        st.write(f"SPRX current price: ${sprx_price:.2f}")
        st.write(f"SPRX shares bought this month: {abs(asset_df['SPRX'])/sprx_price:.4f}")
    except Exception as e:
        st.warning(f"Could not fetch SPRX price: {e}")

st.header('Upload Your Financial Excel File')
uploaded_file = st.file_uploader('Choose an Excel file', type=['xlsx', 'xls'])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write('Preview of your data:')
    st.dataframe(df)
    # Optionally, add editing features here

# --- Positions Upload Section ---
st.header('Upload Your Daily Positions File')
positions_file = st.file_uploader('Upload your daily positions CSV', type=['csv'], key='positions')
if positions_file is not None:
    pos_df = pd.read_csv(positions_file, skip_blank_lines=True)
    # Try to find the main data section by looking for 'Instrument' column
    if 'Instrument' not in pos_df.columns:
        # Try to find the header row
        for i, row in pos_df.iterrows():
            if 'Instrument' in row.values:
                pos_df.columns = row.values
                pos_df = pos_df.iloc[i+1:]
                break
    # Clean up and display
    st.subheader('Current Holdings')
    holdings = pos_df[['Instrument', 'Qty', 'Mark', 'Net Liq', 'Account Name']].copy()
    st.dataframe(holdings)
    # Calculate net worth (sum of Net Liq, ignoring non-numeric)
    def parse_money(val):
        if isinstance(val, str):
            val = val.replace('$','').replace(',','').replace('(','-').replace(')','')
        try:
            return float(val)
        except:
            return np.nan
    holdings['Net Liq Num'] = holdings['Net Liq'].apply(parse_money)
    net_worth = holdings['Net Liq Num'].sum(skipna=True)
    st.metric('Estimated Net Worth', f"${net_worth:,.2f}")
