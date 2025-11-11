import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta


# Page config
st.set_page_config(
    page_title="Ecommerce Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)



# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\HP\Desktop\ecommerce_dashboard_project\cleaned_data\cleaned.csv")
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()


# Sidebar filters
st.sidebar.header("📅 Filters")

# Date range filter
min_date = df['order_date'].min()
max_date = df['order_date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# Convert date_range to datetime
if len(date_range) == 2:
    start_date, end_date = date_range
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
else:
    df_filtered = df.copy()



# Category filter
categories = ['All'] + sorted(df_filtered['product_category'].unique().tolist())
selected_category = st.sidebar.selectbox("Product Category", categories)

if selected_category != 'All':
    df_filtered = df_filtered[df_filtered['product_category'] == selected_category]


# Country filter
countries = ['All'] + sorted(df_filtered['customer_country'].unique().tolist())
selected_country = st.sidebar.selectbox("Country", countries)

if selected_country != 'All':
    df_filtered = df_filtered[df_filtered['customer_country'] == selected_country]



# Main header
st.markdown('<h1 class="main-header">📊 Ecommerce Sales Analysis Dashboard</h1>', unsafe_allow_html=True)

# KPI Row
col1, col2, col3, col4 = st.columns(4)



# Calculate KPIs
total_revenue = df_filtered['total_price'].sum()
total_orders = len(df_filtered)
avg_order_value = df_filtered['total_price'].mean()
unique_customers = df_filtered['customer_id'].nunique()

with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${:,.0f}</div>
    </div>
    """.format(total_revenue), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{:,}</div>
    </div>
    """.format(total_orders), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">${:.2f}</div>
    </div>
    """.format(avg_order_value), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Unique Customers</div>
        <div class="kpi-value">{:,}</div>
    </div>
    """.format(unique_customers), unsafe_allow_html=True)

st.markdown("---")


# Charts Row 1
col1, col2 = st.columns(2)

# Chart 1: Monthly Revenue Trend
with col1:
    st.subheader("📈 Monthly Revenue Trend")
    
    monthly_data = df_filtered.groupby(df_filtered['order_date'].dt.to_period('M'))['total_price'].sum().reset_index()
    monthly_data['order_date'] = monthly_data['order_date'].astype(str)
    
    fig1 = px.line(
        monthly_data,
        x='order_date',
        y='total_price',
        labels={'total_price': 'Revenue ($)', 'order_date': 'Month'},
        markers=True
    )
    fig1.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig1, use_container_width=True)



# Chart 2: Category Performance
with col2:
    st.subheader("🏷️ Category Performance")
    
    category_data = df_filtered.groupby('product_category').agg({
        'total_price': 'sum',
        'order_id': 'count'
    }).reset_index()
    
    fig2 = px.bar(
        category_data,
        x='product_category',
        y='total_price',
        color='order_id',
        labels={'total_price': 'Revenue ($)', 'order_id': 'Orders'},
        color_continuous_scale='Blues'
    )
    fig2.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# Charts Row 2
col3, col4 = st.columns(2)

# Chart 3: Traffic Source Pie
with col3:
    st.subheader("📱 Traffic Source Distribution")
    
    traffic_data = df_filtered.groupby('traffic_source')['total_price'].sum().reset_index()
    
    fig3 = px.pie(
        traffic_data,
        values='total_price',
        names='traffic_source',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig3.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig3, use_container_width=True)



# Chart 4: Top Products Table
with col4:
    st.subheader("🏆 Top 10 Products by Revenue")
    
    product_data = df_filtered.groupby(['product_name', 'product_category'])['total_price'].sum()\
        .reset_index().sort_values('total_price', ascending=False).head(10)
    
    fig4 = go.Figure(data=[go.Table(
        header=dict(values=['Product', 'Category', 'Revenue'],
                   fill_color='#1f77b4',
                   font=dict(color='white', size=12),
                   align='left'),
        cells=dict(values=[product_data['product_name'],
                          product_data['product_category'],
                          product_data['total_price'].apply(lambda x: f"${x:,.2f}")],
                   fill_color='lavender',
                   align='left'))
    ])
    fig4.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig4, use_container_width=True)



    # Full Width: Geographic Map
st.markdown("---")
st.subheader("🌍 Customer Geographic Distribution")

# Aggregate by country
country_data = df_filtered.groupby('customer_country').agg({
    'total_price': 'sum',
    'customer_id': 'nunique',
    'order_id': 'count'
}).reset_index()

fig5 = px.choropleth(
    country_data,
    locations='customer_country',
    color='total_price',
    hover_name='customer_country',
    hover_data={'total_price': ':,.0f', 'customer_id': ',', 'order_id': ','},
    locationmode='country names',
    color_continuous_scale='Viridis',
    title='Revenue by Country'
)

fig5.update_layout(
    height=500,
    margin=dict(l=0, r=0, t=50, b=0),
    geo=dict(showframe=False, showcoastlines=False)
)
st.plotly_chart(fig5, use_container_width=True)


# Add download button
st.markdown("---")
st.subheader("💾 Download Filtered Data")
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_ecommerce_data.csv",
    mime="text/csv"
)
