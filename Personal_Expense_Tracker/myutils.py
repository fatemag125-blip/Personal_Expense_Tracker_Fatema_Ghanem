import pandas as pd
import streamlit as st

# Function to calculate total amount of expenses 
def calculate_total_expenses(df):
    return df["Amount"].sum()

# Function to calculate average daily spent
def calculate_average_daily_spend(df):
    if df.empty:
        return 0
    total_spent= calculate_total_expenses(df)
    days_with_expenses=df["Date"].nunique()

    if days_with_expenses == 0:
        return 0
    return total_spent / days_with_expenses
    
# filter by category
def find_category_totals(df):
    return df.groupby("Category")["Amount"].sum().reset_index()

# calculate monthly spending
def calculate_monthly_spending(df):
    today = pd.Timestamp.today()
    current_month_expenses = df[
            (df["Date"].dt.month == today.month) &
            (df["Date"].dt.year == today.year)
        ]
    return current_month_expenses["Amount"].sum()
    
    

