import os
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="E-Commerce Analytics Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS & ANIMATIONS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 6px;
        color: white;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE CONNECTION UTILITY ---
DB_PATH = "ecommerce.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Ensure database exists and is initialized
if not os.path.exists(DB_PATH):
    st.error("[ERROR] Database file `ecommerce.db` not found! Please run your backend setup first.")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("⚡ E-Commerce Engine")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Navigation Panel",
    ["📊 Executive Summary & Views", "📦 Inventory Catalog", "🔍 Advanced SQL (CTEs / Windows)", "📝 System Audit Logs", "🛒 Simulate Order (ACID)"]
)

# ==========================================
# 1. EXECUTIVE SUMMARY & VIEWS
# ==========================================
if app_mode == "📊 Executive Summary & Views":
    st.title("📈 Executive Monthly Summary Dashboard")
    st.markdown("Real-time aggregated view of business performance powered by SQLite SQL Views (`vw_monthly_summary`).")
    
    try:
        conn = get_connection()
        df_summary = pd.read_sql("SELECT * FROM vw_monthly_summary;", conn)
        conn.close()
        
        if df_summary.empty:
            st.warning("No completed orders found yet! Use the 'Simulate Order' tab to place an order.")
        else:
            # Top Metrics Row with Animation
            col1, col2, col3 = st.columns(3)
            total_rev = df_summary['total_revenue'].sum()
            total_ord = df_summary['total_orders'].sum()
            total_buyers = df_summary['unique_buyers'].sum()
            
            col1.metric(label="💰 Cumulative Revenue", value=f"${total_rev:,.2f}", delta="+12.4%")
            col2.metric(label="📦 Total Orders Completed", value=int(total_ord), delta="+5")
            col3.metric(label="👥 Active Unique Buyers", value=int(total_buyers))
            
            st.markdown("---")
            
            # Animated Plotly Charts
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Monthly Revenue Trends")
                fig_rev = px.bar(
                    df_summary, x='order_month', y='total_revenue',
                    text_auto='.2s', color='total_revenue',
                    color_continuousScale='Blues',
                    template='plotly_dark'
                )
                fig_rev.update_layout(transition_duration=500)
                st.plotly_chart(fig_rev, use_container_width=True)
                
            with col_b:
                st.subheader("Monthly Order Volume")
                fig_ord = px.line(
                    df_summary, x='order_month', y='total_orders',
                    markers=True, template='plotly_dark'
                )
                fig_ord.update_traces(line_color='#3b82f6', line_width=3)
                st.plotly_chart(fig_ord, use_container_width=True)
                
            st.subheader("Raw Summary Data Table")
            st.dataframe(df_summary, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading view: {e}")

# ==========================================
# 2. INVENTORY CATALOG
# ==========================================
elif app_mode == "📦 Inventory Catalog":
    st.title("📦 Product Inventory Management")
    st.markdown("Browse current product stock levels, categories, and pricing catalogs.")
    
    conn = get_connection()
    df_prod = pd.read_sql("SELECT * FROM Products;", conn)
    conn.close()
    
    category_filter = st.selectbox("Filter by Category", ["All"] + list(df_prod['category'].unique()))
    if category_filter != "All":
        df_prod = df_prod[df_prod['category'] == category_filter]
        
    st.dataframe(
        df_prod.style.highlight_max(subset=['stock_qty'], color='#1e3a8a'),
        use_container_width=True
    )

# ==========================================
# 3. ADVANCED SQL (CTEs / WINDOW FUNCTIONS)
# ==========================================
elif app_mode == "🔍 Advanced SQL (CTEs / Window Functions)":
    st.title("⚡ Advanced Analytics Engine")
    st.markdown("Executing declarative complex queries with **Common Table Expressions (CTEs)** and **Window Functions (`RANK()`, `SUM OVER`)**.")
    
    try:
        path = os.path.join("sql", "analytics_queries.sql")
        with open(path, "r", encoding="utf-8") as f:
            script_content = f.read()
            
        queries = [q.strip() for q in script_content.split(";") if q.strip()]
        
        query_choice = st.selectbox(
            "Select Analytical Report Query:",
            [f"Query #{i+1}: {q[:60]}..." for i, q in enumerate(queries)]
        )
        
        selected_idx = int(query_choice.split(":")[0].replace("Query #", "")) - 1
        active_query = queries[selected_idx]
        
        st.code(active_query, language="sql")
        
        if st.button("🚀 Execute Analytics Query", type="primary"):
            conn = get_connection()
            df_result = pd.read_sql(active_query, conn)
            conn.close()
            
            st.success("Query executed successfully!")
            st.dataframe(df_result, use_container_width=True)
            
            # Render visual chart if numeric data is available
            if len(df_result.columns) >= 2 and pd.api.types.is_numeric_dtype(df_result.iloc[:, 1]):
                fig = px.bar(
                    df_result.head(15), 
                    x=df_result.columns[0], 
                    y=df_result.columns[1],
                    color=df_result.columns[1],
                    template='plotly_dark'
                )
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error parsing analytics queries: {e}")

# ==========================================
# 4. SYSTEM AUDIT LOGS
# ==========================================
elif app_mode == "📝 System Audit Logs":
    st.title("🛡️ Immutable Audit Trail & Compliance Log")
    st.markdown("Tracks all transactional operations, CRUD updates, and rollback failure events.")
    
    conn = get_connection()
    df_logs = pd.read_sql("SELECT * FROM AuditLogs ORDER BY executed_at DESC;", conn)
    conn.close()
    
    action_filter = st.selectbox("Filter by Action Type", ["All"] + list(df_logs['action'].unique()))
    if action_filter != "All":
        df_logs = df_logs[df_logs['action'] == action_filter]
        
    st.dataframe(df_logs, use_container_width=True)

# ==========================================
# 5. SIMULATE ORDER (ACID TRANSACTION)
# ==========================================
elif app_mode == "🛒 Simulate Order (ACID Transaction)":
    st.title("🛒 ACID Transaction Simulation (Place Order)")
    st.markdown("Test atomic transaction processing, inventory decrementing, and automatic safety rollbacks.")
    
    conn = get_connection()
    customers = pd.read_sql("SELECT customer_id, name FROM Customers LIMIT 20;", conn)
    products = pd.read_sql("SELECT product_id, product_name, price, stock_qty FROM Products LIMIT 30;", conn)
    conn.close()
    
    with st.form("order_form"):
        selected_cust = st.selectbox("Select Customer", options=customers['customer_id'], format_func=lambda x: f"ID {x}: {customers[customers['customer_id']==x]['name'].values[0]}")
        selected_prod = st.selectbox("Select Product", options=products['product_id'], format_func=lambda x: f"ID {x}: {products[products['product_id']==x]['product_name'].values[0]} (Stock: {products[products['product_id']==x]['stock_qty'].values[0]})")
        quantity = st.number_input("Desired Quantity", min_value=1, max_value=500, value=1)
        
        submit_btn = st.form_submit_button("⚡ Submit Order Transaction")
        
        if submit_btn:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                conn.execute("BEGIN TRANSACTION;")
                cursor.execute("SELECT price, stock_qty FROM Products WHERE product_id = ?;", (selected_prod,))
                prod = cursor.fetchone()
                
                if not prod:
                    conn.rollback()
                    st.error("[ERROR] Product not found. Transaction rolled back.")
                elif prod[1] < quantity:
                    conn.rollback()
                    # Independent log write simulation for UI
                    temp_conn = sqlite3.connect(DB_PATH)
                    temp_conn.execute("INSERT INTO AuditLogs (action, status_message) VALUES (?, ?);", 
                                      ('FAILED_ORDER', f"Stock failure for Product {selected_prod}. Requested: {quantity}, Available: {prod[1]}"))
                    temp_conn.commit()
                    temp_conn.close()
                    st.error(f"❌ [ERROR] Insufficient stock! Requested {quantity}, but only {prod[1]} available. Transaction rolled back and failure logged.")
                else:
                    subtotal = prod[0] * quantity
                    date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    cursor.execute("UPDATE Products SET stock_qty = stock_qty - ? WHERE product_id = ?;", (quantity, selected_prod))
                    cursor.execute("INSERT INTO Orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, 'Completed');", (selected_cust, date, subtotal))
                    oid = cursor.lastrowid
                    cursor.execute("INSERT INTO OrderDetails (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?);", (oid, selected_prod, quantity, prod[0], subtotal))
                    cursor.execute("INSERT INTO AuditLogs (action, status_message) VALUES ('PLACE_ORDER', ?);", (f"Placed Order #{oid}",))
                    
                    conn.commit()
                    st.success(f"🎉 Order #{oid} placed successfully! Subtotal: ${subtotal:.2f}")
            except Exception as e:
                conn.rollback()
                st.error(f"Transaction exception: {e}")
            finally:
                conn.close()