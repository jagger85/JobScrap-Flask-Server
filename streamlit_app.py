import streamlit as st
import datetime

def main():
    st.set_page_config(page_title="Job Scraper", layout="centered")
        
    # Add custom CSS for the container
    st.markdown("""
        <style>
        .custom-container {
            border: 1px solid #ccc;
            border-radius: 2px;
            padding: 20px;
            margin: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create a container with a custom class
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        
    # App content starts here
    st.title("Job scraper")
    
    # Keywords input
    keywords = st.text_input("Enter the keywords", placeholder="e.g. React, Angular, JavaScript")
    
    # Time period selection with select
    st.markdown("<h4 style='text-align: center;'>Select time period</h4>", unsafe_allow_html=True)
    time_period = st.selectbox(
        "",
        ["Last week", "Last month"],
        index=1  # Default to "Last month"
    )
    
    # Platform selection with better alignment
    st.markdown("<h3 style='text-align: center;'>Select platforms</h3>", unsafe_allow_html=True)
    
    # Create two rows of three checkboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        linkedin = st.checkbox("LinkedIn")
        kalibrr = st.checkbox("Kalibrr")
    with col2:
        indeed = st.checkbox("Indeed")
        google = st.checkbox("Google")
    with col3:
        jobstreet = st.checkbox("Jobstreet")
        all_platforms = st.checkbox("All")
    
    # Center the button using markdown and HTML
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start data collection", use_container_width=True):
            with st.spinner("Gathering data... please wait"):
                # Simulate data collection
                progress_bar = st.progress(0)
                for i in range(100):
                    # Update progress bar
                    progress_bar.progress(i + 1)
                st.success("Data collection complete!")
            
            # Enable download button after data collection
            st.download_button(
                label="Download file",
                data="Your scraped job data would be here",
                file_name="job_data.csv",
                mime="text/csv",
                use_container_width=True
            )

    # End of custom container
    st.markdown('</div>', unsafe_allow_html=True)
        
    # CSS for centering the checkboxes
    st.markdown("""
        <style>
        div[data-testid="column"] {
            display: flex;
            justify-content: center;
        }
        div.row-widget.stCheckbox {
            justify-content: center;
            min-width: 150px;
        }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
