import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='darkgrid')

# Load dataset
df = pd.read_csv("data/day_cleaned.csv")

# Mapping
year_mapping = {0: 2011, 1: 2012}
df['yr'] = df['yr'].map(year_mapping)

season_mapping = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
df['season'] = df['season'].map(season_mapping)
season_order = ['Semi', 'Panas', 'Gugur', 'Dingin']
df['season'] = pd.Categorical(df['season'], categories=season_order, ordered=True)

weathersit_mapping = {1: 'Cerah', 2: 'Berawan', 3: 'Badai'}
df['weathersit'] = df['weathersit'].map(weathersit_mapping)
weathersit_order = ['Cerah', 'Berawan', 'Badai']
df['weathersit'] = pd.Categorical(df['weathersit'], categories=weathersit_order, ordered=True)

weekday_mapping = {
    0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu',
    4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
}
df['weekday'] = df['weekday'].map(weekday_mapping)
df['weekday'] = pd.Categorical(df['weekday'], categories=list(weekday_mapping.values()), ordered=True)

workingday_mapping = {0: 'Tidak', 1: 'Ya'}
df['workingday'] = df['workingday'].map(workingday_mapping)
df['workingday'] = pd.Categorical(df['workingday'], categories=['Tidak', 'Ya'], ordered=True)

# Memasitkan dteday dalam tipe data datetime
df['dteday'] = pd.to_datetime(df['dteday'])

# Sidebar untuk filter tanggal
st.sidebar.title(":bike: Bike Sharing Dashboard")
with st.sidebar:
    st.write("Gunakan filter ini untuk menyaring data berdasarkan rentang tanggal, musim, atau kondisi cuaca.")

min_date = df['dteday'].min()
max_date = df['dteday'].max()

start_date, end_date = st.sidebar.date_input(
    label="Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Memastikan start dan end date dalam tipe data datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# filter dataset sesuai tanggal
try:
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = df[(df['dteday'] >= start_date) & (df['dteday'] <= end_date)]
except Exception as e:
    st.error(f"Terjadi kesalahan pada input tanggal: {e}")
    filtered_df = df  # Kembali ke data penuh jika terjadi error


# Filter Musim
season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=df['season'].unique(),
    default=df['season'].unique()
)

# Filter Kondisi Cuaca
weather_filter = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    options=df['weathersit'].unique(),
    default=df['weathersit'].unique()
)

# Terapkan filter tambahan
filtered_df = filtered_df[
    (filtered_df['season'].isin(season_filter)) &
    (filtered_df['weathersit'].isin(weather_filter))
]

# dashboard utama
st.title('Bike Sharing Dashboard :bike:')

# Overview Metrics
st.subheader('Overview Metrics')
total_rides = filtered_df['cnt'].sum()
average_rides = filtered_df['cnt'].mean()
total_casual = filtered_df['casual'].sum()
total_registered = filtered_df['registered'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Rides", f"{total_rides:,}")
    st.metric("Average Rides per Day", f"{round(average_rides):,}")
with col2:
    st.metric("Casual", f"{total_casual:,}")
    st.metric("Registered", f"{total_registered:,}")

# Daily Rides Line Chart
st.subheader("Daily Rides")
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(filtered_df['dteday'], filtered_df['cnt'], marker='o', color='blue')
ax.set_title('Daily Bike Rides', fontsize=16)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Number of Rides', fontsize=12)
ax.grid(True)
st.pyplot(fig)

# rentals by seasons 
st.subheader("Jumlah Penyewa Sepeda Berdasarkan Musim")
season_data = df.groupby('season')[['registered', 'casual']].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(season_data['season'], season_data['registered'], label='Registered', color='#004c6d', bottom=season_data['casual'])
ax1.bar(season_data['season'], season_data['casual'], label='Casual', color='#6996b3')
ax1.set_title('Jumlah Penyewa Sepeda Berdasarkan Musim')
ax1.set_xlabel(None)
ax1.set_ylabel(None)
ax1.legend()
st.pyplot(fig1)

# rentals by weather conditions
st.subheader("Jumlah Pengguna Sepeda Berdasarkan Kondisi Cuaca")
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(
    x='weathersit',
    y='cnt',
    hue='yr',
    data=df,
    ax=ax2,
    palette= ['#6996b3', '#004c6d']
)
ax2.set_title('Jumlah Pengguna Sepeda Berdasarkan Kondisi Cuaca')
ax2.set_xlabel(None)
ax2.set_ylabel(None)
st.pyplot(fig2)

# rentals by days
st.subheader("Pengelompokan Peminjaman Berdasarkan Hari")
grouped_by_weekday = df.groupby(by="weekday").agg({"cnt": "sum"})
fig, ax = plt.subplots()
grouped_by_weekday.plot(kind="bar", ax=ax, legend=False)
ax.set_title("Pengelompokan Berdasarkan Hari")
ax.set_xlabel("Hari")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)

# rentals by working day
st.subheader("Pengelompokan Peminjaman Berdasarkan Hari Kerja")
grouped_by_workingday = df.groupby(by="workingday").agg({"cnt": "sum"})
fig, ax = plt.subplots()
grouped_by_workingday.plot(kind="bar", ax=ax, legend=False)
ax.set_title("Pengelompokan Berdasarkan Hari Kerja")
ax.set_xlabel("Hari Kerja")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)
