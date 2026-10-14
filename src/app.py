import streamlit as st
import snowflake.connector
import os
from dotenv import load_dotenv

# 1. Crack open the secret vault (.env)
load_dotenv()

st.title("❄️ Snowflake DB Clone Tool")

target_db = st.text_input("Target DB name", value="YOUR_DB_NAME_WITH_YOUR_NAME")
source_db = st.text_input("Clone from DB", value="DEV")

owner_role = st.selectbox("Owner role", options=["USERADMIN", "PUBLIC", "SYSADMIN"])
readonly_role = st.text_input("Read-only role", value="read_only_role")

st.warning(f"⚠️ {target_db} already exists (owner: {owner_role}). It will be dropped and recreated if you proceed.")

st.button("🔄 Refresh SQL")

st.header("Generated SQL")
st.subheader("Please, always check db names you set up!")

# The SQL Brain
sql_preview = f"""
DROP DATABASE IF EXISTS {target_db};
CREATE DATABASE {target_db} CLONE {source_db};
GRANT OWNERSHIP ON DATABASE {target_db} TO ROLE {owner_role} REVOKE CURRENT GRANTS;
GRANT USAGE ON DATABASE {target_db} TO ROLE {readonly_role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {target_db} TO ROLE {readonly_role};
GRANT SELECT ON ALL TABLES IN DATABASE {target_db} TO ROLE {readonly_role};
"""

st.code(sql_preview, language="sql")

# 2. The Launch Sequence
if st.button("🚀 Execute SQL"):
    try:
        # Establish the secure connection to the mothership
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
        )
        
        # Streamlit spinner gives UI feedback while the query runs
        with st.spinner("Cloning database... Hold onto your butts!"):
            # execute_string is crucial here because we are running multiple SQL statements at once
            conn.execute_string(sql_preview)
            
        st.success(f"✅ Boom! {target_db} successfully cloned and permissions locked in.")
        
    except Exception as e:
        # If something breaks (like a bad password or missing DB), print the error gracefully
        st.error(f"❌ Mission Failed: {e}")
        
    finally:
        # Always close the connection so you don't leave ghost sessions hanging in Snowflake
        if 'conn' in locals():
            conn.close()