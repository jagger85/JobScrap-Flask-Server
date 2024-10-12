# import streamlit as st
# st.title("Job sweep")
# url = st.text_input("Enter a Website Url: ")

# if st.button("Scrape Site:"):
#     st.write("Scraping the website")
#     result = scrape_website(url)
#     print(result)

from kalibrr import scrape_kalibrr

result = scrape_kalibrr(['react','angular'])
