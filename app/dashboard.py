# Import required libraries
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium

from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from sklearn.cluster import KMeans

# Page configuration
st.set_page_config(
    page_title="Road Accident Hotspot GIS Dashboard",
    layout="wide"
)

# Dashboard title
st.title("Road Accident Hotspot GIS Dashboard")

st.write("""
This dashboard analyzes road accident locations using GIS mapping,
severity analysis, and KMeans hotspot clustering.
""")

# Correct dataset path
current_dir = os.path.dirname(__file__)
data_path = os.path.join(current_dir, "..", "data", "accidents.csv")

# Load dataset
df = pd.read_csv(data_path)

# Remove missing coordinates
df = df.dropna(subset=["Latitude", "Longitude"])

# Use sample for performance
sample_df = df.sample(n=5000, random_state=42)

# Dataset overview
st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Records", f"{len(df):,}")
col2.metric("Sample Used for Map", f"{len(sample_df):,}")
col3.metric("Total Columns", df.shape[1])

st.dataframe(df.head())

# Severity distribution
st.subheader("Accident Severity Distribution")

severity_counts = df["Accident_Severity"].value_counts()

fig1, ax1 = plt.subplots(figsize=(8, 5))
severity_counts.plot(kind="bar", ax=ax1)

ax1.set_title("Accident Severity Distribution")
ax1.set_xlabel("Severity")
ax1.set_ylabel("Number of Accidents")

st.pyplot(fig1)

# Create tabs
tab1, tab2 = st.tabs(["Accident Cluster Map", "KMeans Hotspot Map"])

# Marker cluster map
with tab1:
    st.subheader("Interactive Accident Cluster Map")

    cluster_map = folium.Map(
        location=[
            sample_df["Latitude"].mean(),
            sample_df["Longitude"].mean()
        ],
        zoom_start=6
    )

    marker_cluster = MarkerCluster().add_to(cluster_map)

    for _, row in sample_df.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"Severity: {row['Accident_Severity']}"
        ).add_to(marker_cluster)

    st_folium(cluster_map, width=1100, height=600)

# KMeans hotspot map
with tab2:
    st.subheader("KMeans Accident Hotspot Map")

    location_data = sample_df[["Latitude", "Longitude"]]

    kmeans = KMeans(n_clusters=5, random_state=42)
    sample_df["Cluster"] = kmeans.fit_predict(location_data)

    hotspot_map = folium.Map(
        location=[
            sample_df["Latitude"].mean(),
            sample_df["Longitude"].mean()
        ],
        zoom_start=6
    )

    for _, row in sample_df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=3,
            popup=f"Severity: {row['Accident_Severity']} | Cluster: {row['Cluster']}",
            fill=True,
            fill_opacity=0.7
        ).add_to(hotspot_map)

    st_folium(hotspot_map, width=1100, height=600)

    st.subheader("Accident Count by Hotspot Cluster")
    cluster_counts = sample_df["Cluster"].value_counts().sort_index()
    st.dataframe(cluster_counts)

# Project summary
st.subheader("Project Summary")

st.write("""
This project demonstrates how GIS mapping and machine learning clustering
can be used to identify road accident hotspots. The dashboard supports
public safety analysis by visualizing accident severity patterns and
high-density accident regions.
""")