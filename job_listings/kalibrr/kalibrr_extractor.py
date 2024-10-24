from bs4 import BeautifulSoup

def clean_DOM():
    with open('rawDOM.html', 'r', encoding='utf-8') as file:
        raw_content = file.read()
        soup = BeautifulSoup(raw_content, 'html.parser')
        tags_to_remove = ['script', 'style','head','svg','path']

        # Remove unwanted tags
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()

        cleaned_DOM = soup.prettify()

        # Write cleaned content to file
        with open('cleaned_DOM.html', 'w', encoding='utf-8') as cleaned_file:
            cleaned_file.write(cleaned_DOM)
            print("Cleaned DOM has been saved to 'cleaned_DOM.html'")

if __name__ == "__main__":
    clean_DOM()