Robocaller Detection and Analysis Dashboard

A Streamlit-based web application that detects potential robocallers from call log data using behavior-based thresholds and a Machine Learning (Random Forest) model.

🚀 Features

📁 Upload call logs CSV file

✅ Data validation and preprocessing

📈 Outgoing call count & average call duration analysis

📊 Visualizations: Bar Chart, Pie Chart, Network Graph

🎯 Threshold-based robocaller detection

🤖 Machine Learning-based detection (Random Forest)

📉 Confusion Matrix and accuracy display

⬇️ Downloadable CSV report of detected robocallers

🌐 Live deployed on Streamlit Cloud

📦 Tech Stack

Frontend/UI: Streamlit

Data Handling: Pandas

Graph Analysis: NetworkX

Visualization: Matplotlib, Seaborn

Machine Learning: scikit-learn

Deployment: Streamlit Cloud

📂 File Structure

project/
├── robocaller_dashboard.py         # Main Streamlit app
├── requirements.txt                # Python dependencies
├── logo.png                        # App logo (optional)
└── .streamlit/
    └── config.toml                # Theme configuration

🔧 Setup Instructions

Clone the repository:

git clone https://github.com/yourusername/robocaller_dashboard.git
cd robocaller_dashboard

Install dependencies:

pip install -r requirements.txt

Run the Streamlit app:

streamlit run robocaller_dashboard.py

📁 Sample Input Format (call_logs.csv)

caller_id,receiver_id,call_duration_sec
1001,1002,15
1001,1003,8
1004,1005,300
... etc

📸 Screenshots

(Optional: Insert screenshots of your dashboard if available)

🧠 Future Improvements

Use real-world datasets from telecom sources

Add more ML models like XGBoost

Real-time streaming data support

User authentication & admin panel

📝 License

This project is for academic and learning purposes only.

🙌 Acknowledgements

Built with ❤️ using Python and Streamlit by [venkatakrishnan M].

