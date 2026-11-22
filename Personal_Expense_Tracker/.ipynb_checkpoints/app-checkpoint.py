
import streamlit as st
import pandas as pd
import plotly.express as px

# Import reusable calculation functions from myutils.py
from myutils import (
    calculate_total_expenses,
    calculate_average_daily_spend,
    find_category_totals,
    calculate_monthly_spending
)


# Initializing the expenses DataFrame when the app first starts
# Load existing expense records from the CSV file
if "expenses" not in st.session_state:
    try:
        st.session_state.expenses = pd.read_csv(
            "spend_tracker.csv",
            parse_dates=["Date"]
        )

    # Create an empty DataFrame if the CSV file does not exist
    except FileNotFoundError:
        st.session_state.expenses = pd.DataFrame(
            columns=["Date", "Description", "Category", "Amount", "Payment_Method"]
        )

    # Handle an empty CSV file
    except pd.errors.EmptyDataError:
        st.session_state.expenses = pd.DataFrame(
            columns=["Date", "Description", "Category", "Amount", "Payment_Method"]
        )


# To Track whether an uploaded expense table should be displayed
if "show_expense_table" not in st.session_state:
    st.session_state.show_expense_table = False


# Initializing the monthly budget
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 0.0


# Sidebar navigation allows users to switch between application pages
with st.sidebar:
    st.title("💰 Expense Tracker 💰")

    page_chosen = st.radio(
        "MENU",
        (
            "Home Page",
            "Log Expense",
            "Financial Dashboard",
            "Category Filter",
            "View All"
        )
    )


#  Home Page 

if page_chosen == "Home Page":
    st.title("Personal Expense Tracker")
    st.write("Track your daily expenses and manage your budget.")

    # Allow users to upload an existing CSV file
    st.subheader("Import Expenses")

    uploaded_file = st.file_uploader(
        "Upload your expense CSV file",
        type=["csv"]
    )

    # Process the uploaded file only when the user clicks Load CSV
    if uploaded_file is not None and st.button("Load CSV"):
        try:
            uploaded_expenses = pd.read_csv(uploaded_file)

            # Define the columns required for the expense tracker
            required_columns = [
                "Date", "Description", "Category",
                "Amount", "Payment_Method"
            ]

            # Check whether the uploaded file is empty
            if uploaded_file.size == 0:
                st.error("The uploaded file is empty.")

            # Make sure the uploaded CSV contains all required columns
            elif not all(column in uploaded_expenses.columns for column in required_columns):
                st.error("Invalid CSV file. Please upload a file with all required columns.")

            else:
                # Convert the Date column into datetime format
                uploaded_expenses["Date"] = pd.to_datetime(
                    uploaded_expenses["Date"],
                    errors="raise"
                )

                # Convert the Amount column into numeric values
                uploaded_expenses["Amount"] = pd.to_numeric(
                    uploaded_expenses["Amount"],
                    errors="raise"
                )

                # Check that all expense amounts are valid and greater than zero
                if (
                    uploaded_expenses["Amount"].isna().any()
                    or (uploaded_expenses["Amount"] <= 0).any()
                ):
                    st.error("The CSV contains invalid expense amounts.")

                else:
                    # Store the uploaded expenses in session state
                    st.session_state.expenses = uploaded_expenses[required_columns].copy()

                    # Display the editable table after a successful upload
                    st.session_state.show_expense_table = True

                    st.success("Expenses uploaded successfully!")

        # Handle invalid dates or numeric values
        except ValueError:
            st.error("The CSV contains invalid dates or amounts.")

        # Handle empty or unreadable CSV files
        except pd.errors.EmptyDataError:
            st.error("The uploaded CSV file is empty or invalid.")

        # Handle any other unexpected upload errors
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # Display the uploaded expenses in an editable table
    if st.session_state.show_expense_table:
        st.subheader("Manage Your Expenses")

        edited_expenses = st.data_editor(
            st.session_state.expenses,
            num_rows="dynamic",
            use_container_width=True
        )

        # Update session state with any changes made to the table
        st.session_state.expenses = edited_expenses

    # Allow users to download their current expense records as a CSV file
    st.subheader("Export Expenses")

    csv = st.session_state.expenses.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="spend_tracker.csv",
        mime="text/csv",
        icon=":material/download:"
    )


# Log Expense Page 

elif page_chosen == "Log Expense":
    st.title("Log a New Expense")

    # Take expense details from the user
    date = st.date_input("Expense Date")

    description = st.text_input(
        "What did you spend on?"
    )

    # Let the user choose an expense category
    category = st.selectbox(
        "Select Expense Category",
        (
            "Food & Groceries",
            "Transportation",
            "Utilities",
            "Entertainment",
            "Shopping",
            "Healthcare",
            "Education",
            "Personal Care",
            "Other"
        )
    )

    # Collect the expense amount 
    amount = st.number_input(
        "Amount (BHD)",
        min_value=0.0,
        step=0.100,
        format="%.3f"
    )

    # Let the user select the payment method
    payment_method = st.selectbox(
        "Payment Method",
        (
            "Cash",
            "Debit Card",
            "Credit Card",
            "BenefitPay",
            "Apple Pay"
        )
    )

    # Add the expense when the user clicks the button
    if st.button("Add Expense"):

        # Validate the description and amount before saving
        if description.strip() == "" or amount <= 0:
            st.error("Please enter a description and a valid amount.")

        else:
            # Create a new DataFrame row containing the expense details
            new_row = pd.DataFrame(
                [[date, description, category, amount, payment_method]],
                columns=["Date", "Description", "Category", "Amount", "Payment_Method"]
            )

            # Ensure the date is stored in datetime format
            new_row["Date"] = pd.to_datetime(new_row["Date"])

            # Add the new expense to the existing expense records
            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_row],
                ignore_index=True
            )

            # Save the updated expenses to the CSV file
            st.session_state.expenses.to_csv("spend_tracker.csv", index=False)

            st.success("Expense added successfully!")


# Financial Dashboard Page

elif page_chosen == "Financial Dashboard":
    st.title("Financial Dashboard")

    # Check whether any expenses have been recorded
    if st.session_state.expenses.empty:
        st.info("No expenses recorded yet.")

    else:
        # Calculate the total amount spent using a reusable function
        total_spent = calculate_total_expenses(st.session_state.expenses)

        # Calculate the average spending per day with recorded expenses
        average_daily_spend = calculate_average_daily_spend(st.session_state.expenses)

        # Display the main financial summary in two columns
        col1, col2 = st.columns(2)

        col1.metric(
            "Total Expenditure",
            f"{total_spent:.3f} BHD"
        )

        col2.metric(
            "Average Daily Spending",
            f"{average_daily_spend:.3f} BHD"
        )

        # Calculate total spending for each category
        category_totals = find_category_totals(st.session_state.expenses)

        # Create a pie chart to visualize spending distribution
        fig = px.pie(
            category_totals,
            values="Amount",
            names="Category",
            title="Spending Distribution by Category"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Allow users to set their monthly spending budget
        st.subheader("Monthly Budget")

        monthly_budget = st.number_input(
            "Set your monthly budget (BHD)",
            min_value=0.0,
            step=10.0,
            value=st.session_state.monthly_budget,
            key="budget_input",
            on_change=lambda: setattr(
                st.session_state,
                "monthly_budget",
                st.session_state.budget_input
            )
        )

        # Get the current date to identify the current month
        today = pd.Timestamp.today()

        # Calculate the total expenses recorded during the current month
        current_month_expenses = st.session_state.expenses[
            (st.session_state.expenses["Date"].dt.month == today.month) &
            (st.session_state.expenses["Date"].dt.year == today.year)
        ]

        monthly_spending = calculate_monthly_spending(st.session_state.expenses)

        # Calculate the remaining budget
        remaining_budget = monthly_budget - monthly_spending

        # Display monthly spending and remaining budget
        col1, col2 = st.columns(2)

        col1.metric(
            "Monthly Spending",
            f"{monthly_spending:.3f} BHD"
        )

        col2.metric(
            "Remaining Budget",
            f"{remaining_budget:.3f} BHD"
        )

        # Display a warning when the user approaches or exceeds the budget
        if monthly_budget > 0:
            spending_percentage = (monthly_spending / monthly_budget) * 100

            if spending_percentage >= 100:
                st.error("You have exceeded your monthly budget!")

            elif spending_percentage >= 90:
                st.warning("You have used 90% or more of your monthly budget!")

            else:
                st.success("You are within your monthly budget.")

        # Spending Forecast 

        st.subheader("End of Month Spending Forecast")

        # Calculate the number of days elapsed and total days in the month
        today = pd.Timestamp.today()

        days_elapsed = today.day
        days_in_month = today.days_in_month

        # Estimate end-of-month spending based on the current daily spending rate
        if monthly_spending > 0:
            average_daily_spending = monthly_spending / days_elapsed

            predicted_spending = average_daily_spending * days_in_month

            st.metric(
                "Predicted Monthly Spending",
                f"{predicted_spending:.3f} BHD"
            )

            # Calculate how much additional spending is expected
            predicted_additional_spending = predicted_spending - monthly_spending

            # Compare the predicted spending with the monthly budget
            if monthly_spending > monthly_budget:
                st.warning("You have already exceeded your monthly budget!")

            elif predicted_spending > monthly_budget:
                st.warning(
                    "Based on your current spending rate, "
                    "you may exceed your current monthly budget"
                )

            else:
                st.success("You are likely to stay within budget!")


# Category Filter Page 

elif page_chosen == "Category Filter":
    st.title("Filter Expenses by Category")

    # Allow users to select a category to view
    selected_category = st.selectbox(
        "Choose a category",
        st.session_state.expenses["Category"].unique()
    )

    # Filter the expenses to show only the selected category
    filtered_expenses = st.session_state.expenses[
        st.session_state.expenses["Category"] == selected_category
    ]

    # Calculate the total spending for the selected category
    total_category_spending = filtered_expenses["Amount"].sum()

    st.metric(
        "Total Spending",
        f"{total_category_spending:.3f} BHD"
    )

    # Display the filtered expense records
    st.dataframe(filtered_expenses)


# View All Expenses Page 

elif page_chosen == "View All":
    st.title("All Expenses")

    # Check whether any expense records are available
    if st.session_state.expenses.empty:
        st.info("No expenses recorded yet.")

    else:
        # Display all expenses, with the newest records shown first
        st.dataframe(
            st.session_state.expenses.sort_values(
                by="Date",
                ascending=False
            )
        )
