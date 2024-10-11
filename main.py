import streamlit as st
from scrape import scrape_website

st.title("Job sweep")
url = st.text_input("Enter a Website Url: ")

if st.button("Scrape Site:"):
    st.write("Scraping the website")
    result = scrape_website(url)
    print(result)