import pandas as pd
import streamlit as st

df = pd.read_csv(
            "spend_tracker.csv",
            parse_dates=["Date"]
        )

def calculate_total_expenses(df):
    return df["Amount"].sum()
    
def calculate_average_daily_spend(df):
    if df.empty:
        return 0
    total_spent= calculate_total_expenses(df)
    days_with_expenses=df["Date"].nunique()

    if days_with_expenses == 0:
        return 0
    return total_spent / days_with_expenses

def find_category_totals(df):
    return df.groupby("Category")["Amount"].sum().reset_index()

def calculate_monthly_spending(df):
    today = pd.Timestamp.today()
    current_month_expenses = df[
            (df["Date"].dt.month == today.month) &
            (df["Date"].dt.year == today.year)
        ]
    return current_month_expenses["Amount"].sum()
    
    

