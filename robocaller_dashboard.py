import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score


st.set_page_config(page_title="Robocaller Detection Dashboard", layout="wide")

try:
    logo = Image.open('logo.png')
    st.image(logo, width=150)
except:
    pass

st.title("📞 Robocaller Detection App")

st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "📁 Upload CSV", "📊 Analyze Robocallers"])

if page == "🏠 Home":
    st.header("Welcome to Robocaller Detection Dashboard!")
    st.markdown("""
    🚀 **Detect robocallers easily.**  
    📈 **Analyze call patterns.**  
    📊 **Visualize user engagement.**  
    📥 **Download robocaller reports.**

    👉 Use the sidebar to navigate between different sections!
    """, unsafe_allow_html=True)

elif page == "📁 Upload CSV":
    st.header("📁 Upload your call logs CSV file")
    uploaded_file = st.file_uploader("Upload call_logs.csv", type=["csv"])

    if uploaded_file:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.dataframe(st.session_state['df'].head())
    elif page == "📊 Analyze Robocallers":
     df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Please upload a call_logs.csv file first from 'Upload CSV' page.")
        st.stop()

    else:
        df = st.session_state.get('df')


        required_cols = {'caller_id', 'receiver_id', 'call_duration_sec'}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Invalid CSV format! Required columns: {required_cols}")
            st.stop()

        # Build call graph
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

        # User statistics
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

        st.header("📈 User Call Statistics")
        st.dataframe(df_user_stats)

        # Bar Chart
        st.subheader("📊 Top 10 Callers by Outgoing Calls")
        top_callers = df_user_stats.sort_values('outgoing_calls', ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        top_callers['outgoing_calls'].plot(kind='barh', color='skyblue', ax=ax)
        ax.set_xlabel('Number of Outgoing Calls')
        ax.set_ylabel('User ID')
        ax.set_title('Top 10 Outgoing Callers')
        plt.gca().invert_yaxis()
        st.pyplot(fig)

        # Pie Chart
        st.subheader("🥧 Call Duration Categories (Pie Chart)")
        df['duration_category'] = pd.cut(
            df['call_duration_sec'],
            bins=[0, 20, 60, 300, float('inf')],
            labels=['Very Short', 'Short', 'Medium', 'Long']
        )
        duration_counts = df['duration_category'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(duration_counts, labels=duration_counts.index, autopct='%1.1f%%', startangle=90,
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        ax2.axis('equal')
        st.pyplot(fig2)

        # Network Graph
        st.subheader("🌐 Call Network Graph (Sampled)")
        sampled_edges = list(G.edges(data=True))[:100]
        G_sample = nx.DiGraph()
        G_sample.add_edges_from([(u, v) for u, v, _ in sampled_edges])
        fig3, ax3 = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G_sample, k=0.5)
        nx.draw(G_sample, pos, with_labels=True, node_color='lightblue',
                edge_color='gray', node_size=500, font_size=8, arrows=True)
        st.pyplot(fig3)

        # Threshold-Based Detection
        st.header("🚨 Robocaller Detection Settings")
        st.sidebar.header("🎛️ Detection Thresholds")
        CALL_THRESHOLD = st.sidebar.slider("Minimum outgoing calls", 10, 500, 100, step=10)
        DURATION_THRESHOLD = st.sidebar.slider("Maximum average call duration (seconds)", 5, 60, 20)

        robocallers = df_user_stats[
            (df_user_stats['outgoing_calls'] > CALL_THRESHOLD) &
            (df_user_stats['avg_call_duration'] < DURATION_THRESHOLD)
        ]

        st.subheader("🚨 Detected Robocallers")
        if not robocallers.empty:
            st.success(f"✅ Found {len(robocallers)} potential robocaller(s).")
            st.dataframe(robocallers)

            csv = robocallers.to_csv().encode('utf-8')
            st.download_button(
                label="⬇️ Download Robocallers CSV",
                data=csv,
                file_name='detected_robocallers.csv',
                mime='text/csv'
            )
        else:
            st.info("No robocallers detected with the current thresholds.")

        # ML-Based Detection
        st.header("🤖 Machine Learning Based Detection")

        df_user_stats['is_robocaller'] = (
            (df_user_stats['outgoing_calls'] > 100) &
            (df_user_stats['avg_call_duration'] < 20)
        ).astype(int)

        X = df_user_stats[['outgoing_calls', 'avg_call_duration']]
        y = df_user_stats['is_robocaller']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
