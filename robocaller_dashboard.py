
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ------------------------- APP CONFIG -------------------------
st.set_page_config(page_title="Robocaller Detection Dashboard", layout="wide")
st.title("📞 Robocaller Detection App")

st.markdown("""
Upload a call logs CSV file to analyze users and detect potential robocallers based on:
- High outgoing call count
- Low average call duration
""")

# ------------------------- FILE UPLOAD -------------------------
uploaded_file = st.file_uploader("📁 Upload your call_logs.csv", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # ✅ Validate necessary columns
        required_cols = {'caller_id', 'receiver_id', 'call_duration_sec'}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Invalid CSV format! Required columns: {required_cols}")
            st.stop()

        # ------------------------- DATA PREVIEW -------------------------
        st.subheader("📊 Preview of Uploaded Data")
        st.dataframe(df.head())

        # ------------------------- BUILD GRAPH -------------------------
        G = nx.DiGraph()
        for _, row in df.iterrows():
            caller = row['caller_id']
            receiver = row['receiver_id']
            duration = row['call_duration_sec']

            if G.has_edge(caller, receiver):
                G[caller][receiver]['count'] += 1
                G[caller][receiver]['total_duration'] += duration
            else:
                G.add_edge(caller, receiver, count=1, total_duration=duration)

        # ------------------------- USER STATS -------------------------
        user_stats = {}
        for node in G.nodes:
            edges = G.out_edges(node, data=True)
            total_calls = sum([data['count'] for _, _, data in edges])
            total_duration = sum([data['total_duration'] for _, _, data in edges])
            avg_duration = total_duration / total_calls if total_calls > 0 else 0
            user_stats[node] = {
                'outgoing_calls': total_calls,
                'avg_call_duration': avg_duration
            }

        df_user_stats = pd.DataFrame.from_dict(user_stats, orient='index')

        st.subheader("📈 User Call Statistics")
        st.dataframe(df_user_stats)

        # ------------------------- VISUALIZATION -------------------------
        st.subheader("📊 Top 10 Callers by Outgoing Calls")
        top_callers = df_user_stats.sort_values('outgoing_calls', ascending=False).head(10)

        fig, ax = plt.subplots()
        top_callers['outgoing_calls'].plot(kind='barh', ax=ax, color='steelblue')
        plt.xlabel('Outgoing Calls')
        plt.ylabel('User ID')
        plt.gca().invert_yaxis()
        st.pyplot(fig)

        # ------------------------- THRESHOLD CONTROLS -------------------------
        st.sidebar.header("🎛️ Detection Thresholds")
        CALL_THRESHOLD = st.sidebar.slider("Minimum outgoing calls", 10, 500, 100, step=10)
        DURATION_THRESHOLD = st.sidebar.slider("Max average call duration (seconds)", 5, 60, 20)

        # ------------------------- DETECTION -------------------------
        st.subheader("🚨 Detected Robocallers")
        robocallers = df_user_stats[
            (df_user_stats['outgoing_calls'] > CALL_THRESHOLD) &
            (df_user_stats['avg_call_duration'] < DURATION_THRESHOLD)
        ]

        if not robocallers.empty:
            st.success(f"✅ Found {len(robocallers)} potential robocaller(s).")
            st.dataframe(robocallers)

            # 💾 Download button
            csv = robocallers.to_csv().encode('utf-8')
            st.download_button(
                label="⬇️ Download Robocallers CSV",
                data=csv,
                file_name='detected_robocallers.csv',
                mime='text/csv'
            )
        else:
            st.info("No robocallers detected with the current thresholds.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
