import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_db, save_report, load_reports, update_report_status, delete_report
from engine import analyze_sentiment 

# 1. Page Configuration
st.set_page_config(page_title="EcoPulse | Xpecto '26", layout="wide", page_icon="🌿")

# Initialize the SQL Database
init_db()

# 2. Sidebar Navigation
st.sidebar.title("🌿 EcoPulse v1.2")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Navigation", ["📢 Student Portal", "📊 Admin Dashboard"])

# 3. MODE 1: STUDENT PORTAL
if app_mode == "📢 Student Portal":
    st.title("Campus Sustainability Reporting")
    st.markdown("### Help us make CIT a greener campus.")
    
    with st.form("reporting_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            location = st.selectbox("Location", ["Main Block", "Canteen", "Library", "Hostel A", "Hostel B", "Sports Complex"])
            category = st.selectbox("Issue Category", ["Energy Waste", "Water Leakage", "General Waste", "E-Waste"])
        
        with col2:
            description = st.text_area("Issue Description", placeholder="Please describe the issue (e.g., 'The tap in the 2nd floor washroom is leaking.')")
        
        submit = st.form_submit_button("🚀 Submit Report")

    if submit:
        if description:
            # 🧠 AI PRIORITY CALCULATION (From engine.py)
            priority_score = analyze_sentiment(description)
            
            # Prepare data for SQL
            report_data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'location': location,
                'category': category,
                'description': description,
                'priority': priority_score,
                'sentiment_score': 0.0, # Handled within priority logic
                'status': 'Pending'
            }
            
            # Save to Database
            save_report(report_data)
            st.success(f"Report Logged! Our AI assigned Priority: {priority_score}/10")
            st.balloons()
        else:
            st.warning("Please provide a description of the issue.")

# 4. MODE 2: ADMIN DASHBOARD
else:
    st.title("Management & Analytics Portal")
    
    # Load data from SQL
    df = load_reports()

    # --- SIDEBAR TOOLS: RAPIDMINER EXPORT ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Analytics Tools")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Export for RapidMiner",
            data=csv,
            file_name=f"ecopulse_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            help="Bridge this data into RapidMiner for Predictive Analytics."
        )

    if not df.empty:
        # --- METRICS SECTION ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Reports", len(df))
        m2.metric("Pending Issues", len(df[df['status'] == 'Pending']))
        
        # Calculate Campus Health Index
        pending_count = len(df[df['status'] == 'Pending'])
        health_score = max(0, 100 - (pending_count * 5))
        m3.metric("Campus Health Index", f"{health_score}%")
        
        st.divider()

        # --- CRITICAL ALERTS (High Priority) ---
        critical_issues = df[(df['priority'] >= 7.0) & (df['status'] == 'Pending')]
        if not critical_issues.empty:
            st.error(f"🚨 ALERT: {len(critical_issues)} High-Priority issues need immediate attention!")
            for _, row in critical_issues.iterrows():
                with st.expander(f"🔴 URGENT: {row['category']} at {row['location']} (Score: {row['priority']})"):
                    st.write(f"**Report:** {row['description']}")

        # --- DATA TABLE ---
        st.subheader("Live Issue Logs")
        st.dataframe(df, use_container_width=True)

        # --- ADMIN OPERATIONS (UPDATE & DELETE) ---
        st.divider()
        st.subheader("Database Management")
        
        # Layout for Management Tools
        col_id, col_status, col_upd, col_del = st.columns([1, 2, 1.5, 1.5])
        
        with col_id:
            target_id = st.number_input("Enter ID", min_value=1, step=1)
        
        with col_status:
            new_status = st.selectbox("Set Status", ["Pending", "In Progress", "Resolved"])
        
        with col_upd:
            st.write(" ") # Vertical alignment
            if st.button("🔄 Update Status", use_container_width=True):
                update_report_status(target_id, new_status)
                st.success(f"Report #{target_id} updated!")
                st.rerun()
                
        with col_del:
            st.write(" ") # Vertical alignment
            if st.button("🗑️ Delete Report", use_container_width=True, type="primary"):
                delete_report(target_id)
                st.warning(f"Report #{target_id} permanently deleted.")
                st.rerun()
    else:
        st.info("The database is currently empty. Switch to the Student Portal to add reports.")
