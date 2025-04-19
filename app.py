import streamlit as st
import googlemaps
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page Setup
st.set_page_config(page_title="Hotel Metrics Analyzer", layout="wide")
st.title("🏨 Hotel Metrics & Review Analyzer")

# Google Maps API Setup
API_KEY = st.secrets["GOOGLE_API_KEY"]  # Store your API key in Streamlit secrets

gmaps = googlemaps.Client(key=API_KEY)

# Hotel Input
hotel_name = st.text_input("Enter Hotel or Resort Name:", "Taj Mahal Palace Mumbai")

# Fetch Place Details
@st.cache_data(show_spinner=False)
def get_place_details(hotel_name, location='India'):
    results = gmaps.places(query=f"{hotel_name}, {location}")
    if not results.get('results'):
        return None
    place_id = results['results'][0]['place_id']
    place_details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'rating', 'review'])
    return place_details['result']

@st.cache_data(show_spinner=False)
def extract_reviews(place_data):
    reviews = place_data.get('reviews', [])
    return [{
        'Author': r['author_name'],
        'Rating': r['rating'],
        'Text': r['text'],
        'Time': r['relative_time_description']
    } for r in reviews]

# Generate WordCloud
def generate_wordcloud(texts):
    text_blob = " ".join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_blob)
    return wordcloud

# Process
if st.button("Analyze Hotel"):
    with st.spinner("Fetching data from Google Places API..."):
        place = get_place_details(hotel_name)
        if place:
            st.subheader("📌 Basic Information")
            st.write(f"**Hotel:** {place.get('name')}")
            st.write(f"**Address:** {place.get('formatted_address')}")
            st.write(f"**Rating:** {place.get('rating')} ⭐")

            reviews_data = extract_reviews(place)
            df_reviews = pd.DataFrame(reviews_data)

            if not df_reviews.empty:
                st.subheader("📝 Customer Reviews")
                st.dataframe(df_reviews)

                st.subheader("🔍 WordCloud from Reviews")
                wc = generate_wordcloud(df_reviews['Text'].tolist())
                st.image(wc.to_array(), use_column_width=True)
            else:
                st.warning("No reviews found for this hotel.")
        else:
            st.error("Hotel not found. Try a different name.")

st.sidebar.info("🔐 Add your Google Places API key in Streamlit secrets.")
st.sidebar.code('[secrets]\nGOOGLE_API_KEY = "AIzaSyDijDzINPzK38oZs3uyfjABgxRyYXQ0XQw"')
