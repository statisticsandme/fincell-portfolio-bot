import json
import os
import pandas as pd
import yfinance as yf
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Load credentials
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
client = gspread.authorize(creds)

# Open spreadsheet
SPREADSHEET_ID = "1yJbF9uupRlP8M42qSXKeVFrPdHO3Z_UcOOqvfDRIPnY"
sheet = client.open_by_key(SPREADSHEET_ID)

holdings_ws = sheet.worksheet("Holdings_Master")
cash_ws = sheet.worksheet("Cash_Ledger")
nav_ws = sheet.worksheet("NAV_Daily")
config_ws = sheet.worksheet("Config")

# Load holdings
data = holdings_ws.get_all_records()
df = pd.DataFrame(data)

# Get active tickers
active = df[df["Status"] == "Active"]
tickers = active["Ticker"].tolist()

if tickers:
    prices = yf.download(tickers, period="1d", group_by="ticker", auto_adjust=False)

    for i, row in active.iterrows():
        ticker = row["Ticker"]
        price = prices[ticker]["Close"].iloc[-1]

        df.loc[i, "Current Price"] = round(price, 2)
        df.loc[i, "Market Value"] = round(price * row["Quantity"], 2)
        df.loc[i, "Unrealized P&L"] = round(
            (price - row["Buy Price"]) * row["Quantity"], 2
        )

# Write back to sheet
holdings_ws.update(
    [df.columns.values.tolist()] + df.values.tolist()
)

print("Portfolio updated successfully")

