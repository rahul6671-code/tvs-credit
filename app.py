import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="TVS Residual Engine",layout="wide")
st.title("TVS Dynamic Residual Pricing & Lending Engine")
FILE=Path("TVS_Residual_Lending_Recommendations.csv")
if not FILE.exists():
    st.warning("Run all cells in TVS_Residual_Engine.ipynb first.")
    st.stop()
df=pd.read_csv(FILE)

page=st.sidebar.radio("View",["Portfolio overview","Agreement lookup","Scenario simulator","Model performance","Segment analysis"])
if page=="Portfolio overview":
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Agreements",f"{len(df):,}")
    c2.metric("Avg predicted value",f"₹{df['Predicted Sold Amount'].mean():,.0f}")
    c3.metric("Expected shortfall",f"₹{df['Predicted Shortfall'].sum():,.0f}")
    c4.metric("Avg risk score",f"{df['Residual Risk Score'].mean():.1f}")
    st.bar_chart(df['Residual Risk Band'].value_counts())
elif page=="Agreement lookup":
    agmt=st.selectbox("Agreement ID",df['Agmt Id'].astype(str).tolist())
    row=df[df['Agmt Id'].astype(str)==agmt].iloc[0]
    st.dataframe(row.to_frame("Value"),use_container_width=True)
elif page=="Scenario simulator":
    ev=st.slider("EV adoption shock (%)",0,30,8)/100
    inflation=st.slider("Inflation shock (%)",0,20,4)/100
    fuel=st.slider("Fuel-price shock (%)",0,30,5)/100
    used=st.slider("Used-vehicle price decline (%)",0,30,10)/100
    combined=(.25*ev+.15*inflation+.15*fuel+.45*used)
    stressed=df['Predicted Sold Amount']*(1-combined)
    sf=(df['Loan Amount']-stressed).clip(lower=0)
    c1,c2=st.columns(2)
    c1.metric("Stressed portfolio value",f"₹{stressed.sum():,.0f}")
    c2.metric("Stressed shortfall",f"₹{sf.sum():,.0f}",delta=f"₹{sf.sum()-df['Predicted Shortfall'].sum():,.0f}",delta_color="inverse")
elif page=="Model performance":
    perf=Path("TVS_Model_Performance.csv")
    st.dataframe(pd.read_csv(perf) if perf.exists() else pd.DataFrame(),use_container_width=True)
    st.scatter_chart(df,x="Asset Cost At Disbursal",y="Predicted Sold Amount")
else:
    segment=st.selectbox("Segment",[c for c in ['Asset Model','Asset Fuel Type'] if c in df.columns])
    view=df.groupby(segment).agg(Agreements=('Agmt Id','count'),Average_Risk=('Residual Risk Score','mean'),
            Average_Predicted_Value=('Predicted Sold Amount','mean'),Recommended_LTV=('Recommended LTV','mean')).reset_index()
    st.dataframe(view.sort_values('Agreements',ascending=False),use_container_width=True)
