import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
import os
from babel.numbers import format_currency

#Function untuk menyiapkan berbagai dataframe

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_average_orders_df(df):
    average_orders_df = df.loc[:, ['order_id', 'order_purchase_timestamp']]
    average_orders_df.drop_duplicates()
    
    return average_orders_df

def create_product_df(df):
    product_df = df.loc[:, ['order_id', 'product_category_name']]
    product_df.drop_duplicates()
    
    return product_df

def create_method_df(df):
    method_df = df.loc[:, ['order_id', 'payment_type']]
    
    return method_df

def create_number_product_df(df):
    df['bulan_pembelian'] = df['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp('M')
    number_product_df = df['bulan_pembelian'].value_counts().reset_index()
    number_product_df.columns = ['Bulan - Tahun', 'Jumlah Produk']
    number_product_df = number_product_df.sort_values(by='Bulan - Tahun')

    
    return number_product_df

def create_distribute_month(df):
    date_df = pd.DataFrame({'order_purchase_timestamp': df['order_purchase_timestamp']})

    date_df['year'] = date_df['order_purchase_timestamp'].dt.year
    date_df['month'] = date_df['order_purchase_timestamp'].dt.month
    date_df['day'] = date_df['order_purchase_timestamp'].dt.day

    # Fungsi untuk menggolongkan tanggal
    def classify_day_of_month(day):
        if day <= 10:
            return 'Beginning of the Month'
        elif day <= 20:
            return 'Middle of the Month'
        else:
            return 'End of the Month'

    date_df['day_partition'] = date_df['day'].apply(classify_day_of_month)
    distribute_month = date_df['day_partition'].value_counts()
    
    return distribute_month

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_bycity_df(df):
    city_customer = df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    city_customer.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)
    
    return city_customer

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df['customer_unique_id'] = range(1, len(rfm_df) + 1)
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = pd.to_datetime("2018-09-01").date()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load Data
all_df = pd.read_csv(r'data_all.csv')

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/MuhammadNafishZaldinanda/logo/raw/main/unnamed%20(1).png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# st.dataframe(main_df)

# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)
average_orders_df = create_average_orders_df(main_df)
distribute_month = create_distribute_month(main_df)
product_df = create_product_df(main_df)
method_df = create_method_df(main_df)
number_product_df = create_number_product_df(main_df)
city_customer = create_bycity_df(main_df)

# Plot Jumlah Pesanan
st.header('Olist Store Dashboard')
st.subheader('Number of Orders')

# Menampilkan total pesanan dan total pendapatan
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)

    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "R$", locale='es_CO') 
        st.metric("Total Revenue", value=total_revenue)

# Plot Jumlah Pesanan
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="b"
)
ax.set_title("Number of Orders", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.grid(True)
st.pyplot(fig)

# Plot Total Revenue
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["revenue"],
    marker='o', 
    linewidth=2,
    color="b"
)
ax.set_title("Revenue", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.grid(True)
st.pyplot(fig)

# Plot Jumlah Pesanan Berdasarkan Waktu
st.subheader('Number of Orders Based On Time')

# Plot Jumlah Pesanan Berdasarkan Waktu (Hari, Minggu, Bulan)
with st.container():
    col3, col4, col5 = st.columns(3)

    with col3:
        avg_orders_day = average_orders_df.order_purchase_timestamp.dt.date.value_counts().mean()
        avg_orders_day_rounded = round(avg_orders_day, 2) 
        st.metric("Average Orders Per Day", value=avg_orders_day_rounded)

    with col4:
        avg_orders_week = average_orders_df.order_purchase_timestamp.dt.strftime('%Y-%U').value_counts().mean()
        avg_orders_week_rounded = round(avg_orders_week, 2) 
        st.metric("Average Orders Per Week", value=avg_orders_week_rounded)    

    with col5:
        avg_orders_month = average_orders_df.order_purchase_timestamp.dt.strftime('%Y-%m').value_counts().mean()
        avg_orders_month_rounded = round(avg_orders_month, 2) 
        st.metric("Average Orders Per Month", value=avg_orders_month_rounded)  


# Pie Plot Distribusi Jumlah Pesanan dalam Satu Bulan
labels = distribute_month.index
percentages = ['{:.1f}%'.format((length / sum(distribute_month)) * 100) for length in distribute_month]
data_labels = [f'{percentage}\n({length} Order)' for percentage, length in zip(percentages, distribute_month)]

fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(distribute_month, labels=data_labels, autopct='', wedgeprops={'edgecolor': 'black'})
ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.title('Distribution Number of Orders in One Month', y=1.08)
plt.tight_layout()
st.pyplot(fig)

hari = average_orders_df['order_purchase_timestamp'].dt.day_name().value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
ax.bar(hari.index, hari.values, color=colors)
ax.set_title('Numbers of Orders Across Days of Week', fontsize=14)
ax.set_xlabel('Day of Week', fontsize=12)
ax.set_ylabel('Orders', fontsize=12)
st.pyplot(fig)


# Plot Distribusi Jumlah Pesanan dalam Satu Hari
def categorize_time_of_day(order_purchase_timestamp):
    hour = order_purchase_timestamp.hour
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 20:
        return 'evening'
    else:
        return 'night'
average_orders_df['time_of_day'] = average_orders_df['order_purchase_timestamp'].apply(categorize_time_of_day)

jam = average_orders_df['time_of_day'].value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4"]
ax.bar(jam.index, jam.values, color=colors)
ax.set_title('Numbers of Orders Across Part of Day', fontsize=14)
ax.set_xlabel('Part of Day', fontsize=12)
ax.set_ylabel('Orders', fontsize=12)
st.pyplot(fig)

# Plot Jumlah Customer
st.subheader('Number of Products')

# Plot Jumlah Product
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    number_product_df['Bulan - Tahun'],
    number_product_df['Jumlah Produk'],
    marker='o', 
    linewidth=2,
    color="b"
)
ax.set_title("Number of Products", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.grid(True)
st.pyplot(fig)


# Plot Jumlah Customer
st.subheader('Customer Demographic')

# Plot Jumlah Customer Berdasarkan State
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Plot Jumlah Customer Berdasarkan City
fig, ax = plt.subplots(figsize=(30, 20))
colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data=city_customer.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by City", loc="center", fontsize=40)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=25)
st.pyplot(fig)


# Payment Method
method_payment = method_df['payment_type'].value_counts()
total_orders = len(method_df)  # Total jumlah pesanan

fig, ax = plt.subplots(figsize=(15, 8))
colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4"]
ax.bar(method_payment.index, method_payment.values, color=colors)

for i, value in enumerate(method_payment.values):
    percentage = (value / total_orders) * 100
    ax.text(i, value, f'{percentage:.2f}%', ha='center', va='bottom', fontsize=15)

ax.set_title('Numbers of Orders Across Payment Methods', fontsize=22)
ax.set_xlabel('Payment Method', fontsize=15)
ax.set_ylabel('Orders', fontsize=15)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


# Product performance
kategori_produk_jumlah = product_df['product_category_name'].value_counts().reset_index()
kategori_produk_jumlah.columns = ['Kategori Produk', 'Jumlah']
st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(60, 30))

colors = ["b", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(x="Jumlah", y="Kategori Produk", data=kategori_produk_jumlah.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=50)
ax[0].set_title("Best Performing Product", loc="center", fontsize=70)
ax[0].tick_params(axis='y', labelsize=55)
ax[0].tick_params(axis='x', labelsize=50)

sns.barplot(x="Jumlah", y="Kategori Produk", data=kategori_produk_jumlah.sort_values(by="Jumlah", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=70)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)
st.pyplot(fig)




# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright ©MNafishZ 2023')