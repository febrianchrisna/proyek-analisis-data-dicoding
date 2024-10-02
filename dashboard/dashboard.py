import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('main_data.csv')

data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
data['order_delivered_customer_date'] = pd.to_datetime(data['order_delivered_customer_date'])

st.sidebar.header('Filter Tanggal')
start_date = st.sidebar.date_input('Tanggal Mulai', data['order_purchase_timestamp'].min().date())
end_date = st.sidebar.date_input('Tanggal Akhir', data['order_purchase_timestamp'].max().date())

filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) & 
                     (data['order_purchase_timestamp'].dt.date <= end_date)]

customer_purchase_count = filtered_data.groupby('customer_id').size().reset_index(name='purchase_count')

repeat_customers = customer_purchase_count[customer_purchase_count['purchase_count'] > 1]

repeat_purchases_by_region = pd.merge(
    repeat_customers, 
    filtered_data[['customer_id', 'customer_city', 'customer_state']], 
    on='customer_id'
).groupby(['customer_state', 'customer_city'])['purchase_count'].mean().sort_values(ascending=False)

customer_total_spend = filtered_data.groupby('customer_id')['price'].sum().reset_index()
customer_analysis = pd.merge(customer_purchase_count, customer_total_spend, on='customer_id')

product_ratings = filtered_data.groupby('product_id')['review_score'].mean().sort_values(ascending=False)

category_ratings = filtered_data.groupby('product_category_name')['review_score'].mean().sort_values(ascending=False)

payment_method_ratings = filtered_data.groupby('payment_type')['review_score'].mean().sort_values(ascending=False)

filtered_data['delivery_time'] = (filtered_data['order_delivered_customer_date'] - filtered_data['order_purchase_timestamp']).dt.total_seconds() / 86400  # Konversi ke hari

delivery_time_correlation = filtered_data.groupby('product_id').agg({
    'delivery_time': 'mean',
    'review_score': 'mean'
}).corr()

return_rate = filtered_data.groupby('product_id').agg({
    'order_status': lambda x: ((x == 'canceled') | (x == 'unavailable')).mean(),
    'review_score': 'mean'
}).sort_values('order_status')

st.title("Dashboard Analisis Pembelian Pelanggan :sparkles:")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Gambaran Umum", 
    "Top 10 Daerah", 
    "Rating Produk", 
    "Total Belanja vs Frekuensi Pembelian", 
    "Rating Metode Pembayaran", 
    "Waktu Pengiriman vs Rating Produk", 
    "Tingkat Pengembalian vs Rating Produk",
    "RFM Analysis"
])

with tab1:
    st.metric("Total Pesanan", value=f"{filtered_data['order_id'].nunique()} pesanan")

    daily_orders_df = filtered_data.groupby(filtered_data['order_purchase_timestamp'].dt.date)['order_id'].count().reset_index()
    daily_orders_df.columns = ['order_date', 'order_count']

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(daily_orders_df["order_date"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
    ax.set_title('Jumlah Pesanan per Hari', fontsize=20)
    ax.set_xlabel('Tanggal Pesanan', fontsize=15)
    ax.set_ylabel('Jumlah Pesanan', fontsize=15)
    st.pyplot(fig)

with tab2:
    st.subheader("Top 10 Daerah dengan Rata-rata Pembelian Ulang Tertinggi")
    st.write(repeat_purchases_by_region.head(10))

    fig, ax = plt.subplots(figsize=(10, 6))
    repeat_purchases_by_region.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Daerah dengan Rata-rata Pembelian Ulang Tertinggi')
    ax.set_xlabel('Daerah (State, City)')
    ax.set_ylabel('Rata-rata Pembelian Ulang')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with tab3:
    st.subheader("Produk dengan Rating Tertinggi")
    st.write(product_ratings.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    product_ratings.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Produk dengan Rata-rata Rating Tertinggi')
    ax.set_xlabel('ID Produk')
    ax.set_ylabel('Rata-rata Rating')
    st.pyplot(fig)

    st.subheader("Kategori dengan Rating Tertinggi")
    st.write(category_ratings.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    category_ratings.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Kategori Produk dengan Rata-rata Rating Tertinggi')
    ax.set_xlabel('Nama Kategori')
    ax.set_ylabel('Rata-rata Rating')
    st.pyplot(fig)

with tab4:
    st.subheader("Total Belanja vs Frekuensi Pembelian")
    st.write(customer_analysis.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    plt.scatter(customer_analysis['price'], customer_analysis['purchase_count'])
    plt.title('Hubungan antara Total Belanja dan Frekuensi Pembelian')
    plt.xlabel('Total Belanja')
    plt.ylabel('Jumlah Pembelian')
    st.pyplot(fig)

with tab5:
    st.subheader("Rating Berdasarkan Metode Pembayaran")
    st.write(payment_method_ratings)

    fig, ax = plt.subplots(figsize=(10, 6))
    payment_method_ratings.plot(kind='bar', ax=ax)
    ax.set_title('Rata-rata Rating Berdasarkan Metode Pembayaran')
    ax.set_xlabel('Metode Pembayaran')
    ax.set_ylabel('Rata-rata Rating')
    plt.xticks(rotation=45)
    st.pyplot(fig)

with tab6:
    st.subheader("Hubungan antara Waktu Pengiriman dan Rating Produk")
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.scatter(filtered_data['delivery_time'], filtered_data['review_score'])
    plt.title('Waktu Pengiriman vs Rating Produk')
    plt.xlabel('Waktu Pengiriman (hari)')
    plt.ylabel('Rating Produk')
    st.pyplot(fig)

with tab7:
    st.subheader("Hubungan antara Tingkat Pengembalian dan Rating Produk")
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.scatter(return_rate['order_status'], return_rate['review_score'])
    plt.title('Tingkat Pengembalian vs Rata-rata Rating Produk')
    plt.xlabel('Tingkat Pengembalian')
    plt.ylabel('Rata-rata Rating')
    st.pyplot(fig)

with tab8:
    st.subheader("RFM Analysis")
    
    # Menghitung RFM
    filtered_data['total_price'] = filtered_data['price']
    rfm_df = filtered_data.groupby('customer_id').agg({
        'order_purchase_timestamp': 'max', 
        'order_id': 'nunique', 
        'total_price': 'sum'  
    }).reset_index()

    rfm_df.columns = ['customer_id', 'last_purchase_date', 'frequency', 'monetary']
    rfm_df['last_purchase_date'] = pd.to_datetime(rfm_df['last_purchase_date']).dt.date
    most_recent_date = filtered_data['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['last_purchase_date'].apply(lambda x: (most_recent_date - x).days)
    rfm_df.drop('last_purchase_date', axis=1, inplace=True)

    st.write(rfm_df.head())

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    top_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
    sns.barplot(y="recency", x="customer_id", data=top_recency, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Top 5 Customers by Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis='x', labelsize=15)

    top_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    sns.barplot(y="frequency", x="customer_id", data=top_frequency, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("Top 5 Customers by Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)

    top_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    sns.barplot(y="monetary", x="customer_id", data=top_monetary, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("Top 5 Customers by Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)

    plt.suptitle("Best Customers Based on RFM Parameters (customer_id)", fontsize=20)
    st.pyplot(fig)
