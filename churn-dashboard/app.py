from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv(Path(__file__).parent / "telco-churn.csv")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    df["Churned"] = (df["Churn"] == "Yes").astype(int)
    return df


df = load_data()

st.title("Customer Churn Dashboard")
st.caption("IBM Telco Customer Churn dataset: 7,043 customers. Use the filters on the left to explore who leaves.")

# ---- Sidebar filters ----
st.sidebar.header("Filters")
all_contracts = sorted(df["Contract"].unique())
all_internet = sorted(df["InternetService"].unique())

contracts = st.sidebar.multiselect("Contract type", all_contracts, default=all_contracts)
internet = st.sidebar.multiselect("Internet service", all_internet, default=all_internet)
tenure_range = st.sidebar.slider("Tenure (months)", 0, 72, (0, 72))

f = df[
    df["Contract"].isin(contracts)
    & df["InternetService"].isin(internet)
    & df["tenure"].between(tenure_range[0], tenure_range[1])
]

if f.empty:
    st.warning("No customers match these filters. Try widening them.")
    st.stop()

# ---- Key numbers ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(f):,}")
c2.metric("Churn rate", f"{f['Churned'].mean() * 100:.1f}%")
c3.metric("Average monthly charge", f"{f['MonthlyCharges'].mean():.2f}")
c4.metric("Average tenure (months)", f"{f['tenure'].mean():.1f}")


def churn_bar(column, title, color):
    rate = f.groupby(column)["Churned"].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    rate.plot(kind="bar", ax=ax, color=color)
    ax.set_title(title)
    ax.set_ylabel("Churn rate (%)")
    ax.set_xlabel("")
    plt.xticks(rotation=0)
    plt.tight_layout()
    return fig


# ---- Charts ----
left, right = st.columns(2)
with left:
    st.pyplot(churn_bar("Contract", "Churn rate by contract type", "steelblue"))
with right:
    st.pyplot(churn_bar("InternetService", "Churn rate by internet service", "indianred"))

fig, ax = plt.subplots(figsize=(12, 4))
ax.hist(
    [f.loc[f["Churned"] == 0, "tenure"], f.loc[f["Churned"] == 1, "tenure"]],
    bins=24, stacked=True, label=["Stayed", "Left"], color=["#4c78a8", "#f58518"],
)
ax.set_title("Tenure (months): who leaves and when")
ax.set_xlabel("Tenure (months)")
ax.set_ylabel("Customers")
ax.legend()
plt.tight_layout()
st.pyplot(fig)

with st.expander("Show the data for the selected customers"):
    st.dataframe(f.drop(columns="Churned"))