import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Set page config
st.set_page_config(page_title="Robocaller Detection Dashboard", layout="wide")

# Navigation
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "📤 Upload CSV", "📊 Analyze Robocallers"])

st.title("📞 Robocaller Detection Dashboard")

# Session state to store data
if 'df' not in st.session_state:
    st.session_state['df'] = None

# Home Page
if page == "🏠 Home":
    st.markdown("Welcome to the Robocaller Detection Dashboard!")
    st.markdown("Use the sidebar to upload a CSV file and analyze robocall behavior.")

# Upload Page
elif page == "📤 Upload CSV":
    uploaded_file = st.file_uploader("Upload Call Logs CSV", type=["csv"])
    if uploaded_file:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.dataframe(st.session_state['df'].head())

# Analyze Page
elif page == "📊 Analyze Robocallers":
    df = st.session_state['df']

    if df is None:
        st.warning("⚠️ Please upload a CSV file first.")
    else:
        st.subheader("Call Statistics per Caller")

        # Aggregate call stats
        df_user_stats = df.groupby('caller_id').agg(
            outgoing_calls=('receiver_id', 'count'),
            avg_call_duration=('call_duration_sec', 'mean')
        ).reset_index()

        # Improved robocaller detection threshold
        df_user_stats['is_robocaller'] = (
            (df_user_stats['outgoing_calls'] > 50) &
            (df_user_stats['avg_call_duration'] < 15)
        ).astype(int)

        st.write(df_user_stats.head())

        st.subheader("📊 Robocaller Summary")
        st.bar_chart(df_user_stats['is_robocaller'].value_counts())

        st.subheader("📉 Machine Learning Classification")

        # Prepare features and labels
        X = df_user_stats[['outgoing_calls', 'avg_call_duration']]
        y = df_user_stats['is_robocaller']

        # Avoid error when only one class present
        if len(y.unique()) < 2:
            st.error("❌ Not enough class variety (no robocallers detected). Please upload a better dataset.")
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            st.pyplot(fig)

            st.text("Classification Report:")
            st.code(classification_report(y_test, y_pred))

