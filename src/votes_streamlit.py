import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config.db_conn import db_connection
from config.settings import votes_per_candidate_topic, turnout_by_location_topic
from kafka_repo.consumer_producer import create_kafka_consumer


# Function to fetch voting statistics from PostgreSQL database
@st.cache_data
def fetch_voting_stats():
    conn, cur = db_connection()

    # Fetch total number of voters
    cur.execute("""
        SELECT count(*) voters_count FROM voters
    """)
    voters_count = cur.fetchone()[0]

    # Fetch total number of candidates
    cur.execute("""
        SELECT count(*) candidates_count FROM candidates
    """)
    candidates_count = cur.fetchone()[0]

    return voters_count, candidates_count


def fetch_data_from_kafka(consumer):
    messages = consumer.poll(timeout_ms=1000)
    data = []

    for message in messages.values():
        for sub_message in message:
            data.append(sub_message.value)
    return data


# Function to plot a colored bar chart for vote counts per candidate
def plot_colored_bar_chart(results):
    data_type = results['candidate_name']
    colors = plt.cm.viridis(np.linspace(0, 1, len(data_type)))
    plt.bar(data_type, results['total_votes'], color=colors)
    plt.xlabel('Candidate')
    plt.ylabel('Total Votes')
    plt.title('Vote Counts per Candidate')
    plt.xticks(rotation=90)
    return plt


# Function to plot a donut chart for vote distribution
def plot_donut_chart(data: pd.DataFrame, title='Donut Chart', type='candidate'):
    if type == 'candidate':
        labels = list(data['candidate_name'])
    elif type == 'gender':
        labels = list(data['gender'])

    sizes = list(data['total_votes'])
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    plt.title(title)
    return fig


# Function to plot a pie chart for vote distribution
def plot_pie_chart(data, title='Gender Distribution of Voters', labels=None):
    sizes = list(data.values())
    if labels is None:
        labels = list(data.keys())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    plt.title(title)
    return fig


# Function to split a dataframe into chunks for pagination
@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i: i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df


# Function to paginate a table
def paginate_table(table_data):
    top_menu = st.columns(3)
    with top_menu[0]:
        sort = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=1)
    if sort == "Yes":
        with top_menu[1]:
            sort_field = st.selectbox("Sort By", options=table_data.columns)
        with top_menu[2]:
            sort_direction = st.radio(
                "Direction", options=["⬆️", "⬇️"], horizontal=True
            )
        table_data = table_data.sort_values(
            by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
        )
    pagination = st.container()

    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=[10, 25, 50, 100])
    with bottom_menu[1]:
        total_pages = (
            int(len(table_data) / batch_size) if int(len(table_data) / batch_size) > 0 else 1
        )
        current_page = st.number_input(
            "Page", min_value=1, max_value=total_pages, step=1
        )
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")

    pages = split_frame(table_data, batch_size)
    pagination.dataframe(data=pages[current_page - 1], use_container_width=True)


# Function to update data displayed on the dashboard
def update_data():
    # Placeholder to display last refresh time
    last_refresh = st.empty()
    last_refresh.text(f"Last refreshed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    voters_count, candidates_count = fetch_voting_stats()

    # Display total voters and candidates metrics
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    col1.metric("Total Voters", voters_count)
    col2.metric("Total Candidates", candidates_count)

    # Fetch data from Kafka on aggregated votes per candidate
    consumer = create_kafka_consumer(votes_per_candidate_topic)
    data = fetch_data_from_kafka(consumer)
    results = pd.DataFrame(data)

    # Identify the leading candidate
    results = results.loc[results.groupby('candidate_id')['total_votes'].idxmax()]
    leading_candidate = results.loc[results['total_votes'].idxmax()]

    # Display leading candidate information
    st.markdown("""---""")
    st.header('Leading Candidate')
    col1, col2 = st.columns(2)
    with col1:
        st.image(leading_candidate['photo_url'], width=200)
    with col2:
        st.header(leading_candidate['candidate_name'])
        st.subheader(leading_candidate['party_affiliation'])
        st.subheader("Total Vote: {}".format(leading_candidate['total_votes']))

    # Display statistics and visualizations
    st.markdown("""---""")
    st.header('Statistics')
    results = results[['candidate_id', 'candidate_name', 'party_affiliation', 'total_votes']]
    results = results.reset_index(drop=True)
    col1, col2 = st.columns(2)

    # Display bar chart and donut chart
    with col1:
        bar_fig = plot_colored_bar_chart(results)
        st.pyplot(bar_fig)

    with col2:
        donut_fig = plot_donut_chart(results, title='Vote Distribution')
        st.pyplot(donut_fig)

    # Display table with candidate statistics
    st.table(results)

    # Fetch data from Kafka on aggregated turnout by location
    location_consumer = create_kafka_consumer(turnout_by_location_topic)
    location_data = fetch_data_from_kafka(location_consumer)
    location_result = pd.DataFrame(location_data)

    # Identify locations with maximum turnout
    location_result = location_result.loc[location_result.groupby('state')['count'].idxmax()]
    location_result = location_result.reset_index(drop=True)

    # Display location-based voter information with pagination
    st.header("Location of Voters")
    paginate_table(location_result)

    # Update the last refresh time
    st.session_state['last_update'] = time.time()


# Sidebar layout
def sidebar():
    # Initialize last update time if not present in session state
    if st.session_state.get('last_update') is None:
        st.session_state['last_update'] = time.time()

    # Slider to control refresh interval
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 3, 60, 10)
    st_autorefresh(interval=refresh_interval * 1000, key="auto")

    # Button to manually refresh data
    if st.sidebar.button('Refresh Data'):
        update_data()


# Title of the Streamlit dashboard
st.title('Real-Time Elections Dashboard')
# topic_name = 'aggregated_votes_per_candidate'

# Display sidebar
sidebar()

# Update and display data on the dashboard
update_data()
