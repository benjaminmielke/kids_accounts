import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# -- Configuration Section --
bigquery_secrets = st.secrets["bigquery"]
credentials = service_account.Credentials.from_service_account_info(bigquery_secrets)
PROJECT_ID = bigquery_secrets["project_id"]
DATASET_ID = "budget_data"
TABLE_ID = "kids_accounts"
ACCOUNTS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Use your JSON authentication file for BigQuery.
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

# Function to refresh the account balances from BigQuery.
def load_accounts():
    query = f"SELECT kid_name, available_cash, savings FROM `{ACCOUNTS_TABLE}` ORDER BY kid_name"
    df = client.query(query, location="US").to_dataframe()
    return df

# Function to run an update query on BigQuery.
def update_account(query_text):
    client.query(query_text, location="US").result()  # Wait for query to complete

# -- Styling --
st.markdown(
    """
    <style>
    /* Custom title styling */
    .custom-title {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: blue;
        text-align: center;
        margin: 0;
        padding: 0;
        font-size: 15rem;
    }
    
    /* Base container styling */
    .account-container {
        margin-bottom: 8px;
        padding: 10px;
        background-color: #f2f2f2;
        border-radius: 10px;
        border-bottom-width: 4px;
        border-bottom-style: solid;
    }
    
    /* Kid-specific border colors for containers */
    .haddie-container { border-bottom-color: purple; }
    .jack-container { border-bottom-color: orange; }
    .posey-container { border-bottom-color: pink; }
    
    /* Title bar with white background */
    .title-bar {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* Metric card styling */
    .metric-card {
        background-color: white;
        border-width: 6px;
        border-style: solid;
        border-radius: 8px;
        padding: 20px;
        margin: 10px;
        box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* Card heading */
    .metric-card h3 {
        margin: 0 0 10px 0;
        font-size: 1.75rem;
        color: black;
        text-align: center;
    }
    
    /* Card value */
    .metric-card p {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    /* Kid-specific styles */
    .haddie-color { color: purple !important; }
    .haddie-border { border-color: purple; }
    
    .jack-color { color: orange !important; }
    .jack-border { border-color: orange; }
    
    .posey-color { color: pink !important; }
    .posey-border { border-color: pink; }
    
    /* Button styling */
    .stButton > button {
        width: 100% !important;
        height: 4rem !important;
        font-size: 2.5rem !important;
        margin-top: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Button colors */
    .stButton button:has(div:contains("➕")) {
        background-color: green !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton button:has(div:contains("➖")) {
        background-color: red !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton button:has(div:contains("↔")) {
        background-color: blue !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton button:has(div:contains("%")) {
        background-color: purple !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom title markup
st.markdown('<h1 class="custom-title">💰Mielke Bank💰</h1>', unsafe_allow_html=True)

# Load account data
accounts_df = load_accounts()

# For each kid, display the account
for idx, row in accounts_df.iterrows():
    kid = row["kid_name"]
    available_cash = float(row["available_cash"])
    savings = float(row["savings"])
    
    # Initialize session state toggles if not already set
    for action in ["add", "subtract", "transfer", "interest"]:
        key = f"show_{action}_{kid}"
        if key not in st.session_state:
            st.session_state[key] = False

    # Determine CSS classes based on kid's name
    color_class = ""
    border_class = ""
    container_class = ""
    if kid.lower() == "haddie":
        color_class = "haddie-color"
        border_class = "haddie-border"
        container_class = "haddie-container"
    elif kid.lower() == "jack":
        color_class = "jack-color"
        border_class = "jack-border"
        container_class = "jack-container"
    elif kid.lower() == "posey":
        color_class = "posey-color"
        border_class = "posey-border"
        container_class = "posey-container"
    
    # Container for each kid's account
    st.markdown(f'<div class="account-container {container_class}">', unsafe_allow_html=True)
    
    # Title bar with white background and colored text
    st.markdown(
        f'<div class="title-bar"><h2 style="font-family: \'Comic Sans MS\', sans-serif; margin: 0;" class="{color_class}">{kid}\'s Account</h2></div>',
        unsafe_allow_html=True,
    )
    
    # Two horizontally aligned metric cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card {border_class}">
                <h3>Available Cash</h3>
                <p style="color: green;">${available_cash:,.2f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card {border_class}">
                <h3>Savings</h3>
                <p style="color: blue;">${savings:,.2f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Create four buttons
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("➕", key=f"btn_add_{kid}", use_container_width=True):
            st.session_state[f"show_add_{kid}"] = True
        
    with cols[1]:
        if st.button("➖", key=f"btn_subtract_{kid}", use_container_width=True):
            st.session_state[f"show_subtract_{kid}"] = True
        
    with cols[2]:
        if st.button("↔", key=f"btn_transfer_{kid}", use_container_width=True):
            st.session_state[f"show_transfer_{kid}"] = True
            
    with cols[3]:
        if st.button("%", key=f"btn_interest_{kid}", use_container_width=True):
            st.session_state[f"show_interest_{kid}"] = True
    
    # --- Form for Adding Funds ---
    if st.session_state[f"show_add_{kid}"]:
        with st.form(key=f"add_form_{kid}"):
            add_amount = st.number_input("Amount to Add to Available Cash", min_value=0.0, format="%.2f", key=f"add_input_{kid}")
            submitted = st.form_submit_button("Submit")
            if submitted:
                query_text = f"""
                    UPDATE `{ACCOUNTS_TABLE}`
                    SET available_cash = available_cash + {add_amount}
                    WHERE kid_name = '{kid}'
                """
                update_account(query_text)
                st.success(f"Added ${add_amount:,.2f} to {kid}'s available cash.")
                st.session_state[f"show_add_{kid}"] = False
                st.rerun()  # Auto refresh after submission
        if st.button("Cancel Add", key=f"cancel_add_{kid}"):
            st.session_state[f"show_add_{kid}"] = False
            st.rerun()  # Auto refresh after cancellation

    # --- Form for Subtracting Funds ---
    if st.session_state[f"show_subtract_{kid}"]:
        with st.form(key=f"subtract_form_{kid}"):
            subtract_amount = st.number_input("Amount to Subtract from Available Cash", min_value=0.0, format="%.2f", key=f"subtract_input_{kid}")
            spend_note = st.text_input("Note for Spending", key=f"note_input_{kid}")
            submitted = st.form_submit_button("Submit")
            if submitted:
                query_text = f"""
                    UPDATE `{ACCOUNTS_TABLE}`
                    SET available_cash = available_cash - {subtract_amount}
                    WHERE kid_name = '{kid}'
                """
                update_account(query_text)
                st.success(f"Subtracted ${subtract_amount:,.2f} from {kid}'s available cash for: {spend_note}")
                st.session_state[f"show_subtract_{kid}"] = False
                st.rerun()  # Auto refresh after submission
        if st.button("Cancel Subtract", key=f"cancel_subtract_{kid}"):
            st.session_state[f"show_subtract_{kid}"] = False
            st.rerun()  # Auto refresh after cancellation

    # --- Form for Transferring Funds ---
    if st.session_state[f"show_transfer_{kid}"]:
        # Create separate form keys based on direction to avoid conflicts
        transfer_direction = st.radio(
            "Transfer Direction:",
            ["From Cash to Savings", "From Savings to Cash"],
            key=f"transfer_direction_{kid}"
        )
            
        is_cash_to_savings = "Cash to Savings" in transfer_direction
            
        with st.form(key=f"transfer_form_{kid}_{is_cash_to_savings}"):
            if is_cash_to_savings:
                transfer_amount = st.number_input(
                    "Amount to Transfer from Available Cash to Savings", 
                    min_value=0.0, max_value=float(available_cash), format="%.2f", 
                    key=f"transfer_c2s_{kid}"
                )
                
                submitted = st.form_submit_button("Transfer to Savings")
                if submitted:
                    query_text = f"""
                        UPDATE `{ACCOUNTS_TABLE}`
                        SET available_cash = available_cash - {transfer_amount},
                            savings = savings + {transfer_amount}
                        WHERE kid_name = '{kid}'
                    """
                    update_account(query_text)
                    st.success(f"Transferred ${transfer_amount:,.2f} from available cash to savings for {kid}.")
                    st.session_state[f"show_transfer_{kid}"] = False
                    st.rerun()
            else:
                transfer_amount = st.number_input(
                    "Amount to Transfer from Savings to Available Cash", 
                    min_value=0.0, max_value=float(savings), format="%.2f", 
                    key=f"transfer_s2c_{kid}"
                )
                
                submitted = st.form_submit_button("Transfer to Cash")
                if submitted:
                    query_text = f"""
                        UPDATE `{ACCOUNTS_TABLE}`
                        SET savings = GREATEST(0, savings - {transfer_amount}),
                            available_cash = available_cash + {transfer_amount}
                        WHERE kid_name = '{kid}'
                    """
                    update_account(query_text)
                    st.success(f"Transferred ${transfer_amount:,.2f} from savings to available cash for {kid}.")
                    st.session_state[f"show_transfer_{kid}"] = False
                    st.rerun()
                    
        if st.button("Cancel Transfer", key=f"cancel_transfer_{kid}"):
            st.session_state[f"show_transfer_{kid}"] = False
            st.rerun()  # Auto refresh after cancellation

    # --- Form for Adding Interest ---
    if st.session_state[f"show_interest_{kid}"]:
        # Calculate 10% interest amount
        interest_amount = savings * 0.10
        
        with st.form(key=f"interest_form_{kid}"):
            st.write(f"Add 10% interest (${interest_amount:.2f}) to {kid}'s savings?")
            submitted = st.form_submit_button("Confirm")
            if submitted:
                query_text = f"""
                    UPDATE `{ACCOUNTS_TABLE}`
                    SET savings = savings * 1.10
                    WHERE kid_name = '{kid}'
                """
                update_account(query_text)
                st.success(f"Added ${interest_amount:.2f} (10% interest) to {kid}'s savings.")
                st.session_state[f"show_interest_{kid}"] = False
                st.rerun()  # Auto refresh after submission
        if st.button("Cancel Interest", key=f"cancel_interest_{kid}"):
            st.session_state[f"show_interest_{kid}"] = False
            st.rerun()  # Auto refresh after cancellation
            
    st.markdown("</div>", unsafe_allow_html=True)
