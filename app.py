import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.title("🌸 Fragrance Recommender")
st.write("App is working! Next step: load fragrance data and build recommendations.")

@st.cache_data
def load_data():
    df = pd.read_csv("data/combined_fragrances.csv")
    
    def clean_product_name(row):
        name = row['product_name']
        brand = row['brand_name']
        if pd.notna(brand) and brand in name:
            name = name.split(brand)[0].strip()
        return name
    
    df['product_name'] = df.apply(clean_product_name, axis=1)
    
    df['scent_profile'] = (
        df['top_notes'].fillna('') + ' ' +
        df['middle_notes'].fillna('') + ' ' +
        df['base_notes'].fillna('') + ' ' +
        df['notes'].fillna('') + ' ' +
        df['main_accords'].fillna('')
    )
    return df

@st.cache_data
def build_similarity_matrix(df):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['scent_profile'])
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

def get_recommendations(fragrance_name, df, similarity_matrix, top_n=5):
    idx = df[df['product_name'] == fragrance_name].index[0]

    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[1:top_n+1]

    recommended_indices = [i[0] for i in similarity_scores]
    scores = [i[1] for i in similarity_scores]

    recommendations = df.iloc[recommended_indices].copy()
    recommendations['similarity_score'] = scores

    return recommendations

# Load data and build similarity matrix
df = load_data()
similarity_matrix = build_similarity_matrix(df)

# UI
st.title("🌸 Fragrance Recommender")
st.write("Pick a fragrance you like, and we'll find similar ones based on notes and accords.")

selected_fragrance = st.selectbox(
    "Choose a fragrance:",
    options=sorted(df['product_name'].unique())
)

top_n = st.slider("Number of recommendations:", min_value=3, max_value=10, value=5)

if st.button("Get Recommendations"):
    recommendations = get_recommendations(selected_fragrance, df, similarity_matrix, top_n=top_n)

    st.subheader(f"Fragrances similar to {selected_fragrance}")

    for _, row in recommendations.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            if pd.notna(row['product_images']) and row['product_images'] != 'N/A':
                st.image(row['product_images'], width=100)
        with col2:
            st.markdown(f"**{row['product_name']}** — {row['brand_name']}")
            st.write(f"Accords: {row['main_accords']}")
            st.write(f"Similarity: {row['similarity_score']:.2f}")
        st.divider()