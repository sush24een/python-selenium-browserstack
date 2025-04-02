from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from deep_translator import GoogleTranslator
from collections import Counter
import requests
import os
import time
import re

# Initialize WebDriver and the translator
driver = webdriver.Chrome()  
translator = GoogleTranslator(source="es", target="en")

# Step 1: Open the El País website
driver.get("https://elpais.com/")  
print("El País homepage opened.")  

# Verify page language using the lang attribute
lang = driver.execute_script("return document.documentElement.lang")
if lang.startswith('es'):
    print("Website is in Spanish.")
else:
    print("Website might not be in Spanish.")

# Navigate to Opinion section
driver.get("https://elpais.com/opinion/")  
print("Navigated to the Opinion section.")  

# Wait for articles to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, "//article")))

# Create directories for saving images
# 'article_images' will store the cover images for each article
# 'article_content_images' will store images found within the content of the articles
if not os.path.exists("article_images"):
    os.makedirs("article_images")
if not os.path.exists("article_content_images"):
    os.makedirs("article_content_images")

translated_titles = []  # Store translated titles for analysis

# Step 2: Scrape articles from the "Opinion" Section
for i in range(5):  
    try:
        articles = driver.find_elements(By.XPATH, "//article")
        if i >= len(articles):
            print(f"Warning: Only found {len(articles)} articles.")
            break

        article = articles[i]

        # Extract title
        title_element = article.find_element(By.XPATH, ".//h2/a")  
        title = title_element.get_attribute("textContent").strip()
        link = title_element.get_attribute("href")

        # Step 3: Translate title
        translated_title = translator.translate(title)
        translated_titles.append(translated_title)

        # Extract summary
        # Note: The summary text is not directly accessible in the DOM.
        # textContent extracts text directly from the DOM, ignoring visibility settings.
        try:
            summary_element = article.find_element(By.XPATH, ".//p[contains(@class, 'c_d')]")
            summary = driver.execute_script("return arguments[0].textContent;", summary_element).strip()
            if not summary:
                summary = "Summary exists but is hidden"
        except Exception:
            summary = "No summary available"

        # Extract and save cover image
        img_elements = article.find_elements(By.XPATH, ".//img")  # Find all <img> elements
        if img_elements:  # Check if any <img> element is found
            img_url = img_elements[0].get_attribute("src")  # Get the URL of the first image
            if img_url:
                img_data = requests.get(img_url).content  # Download the image data
                img_path = f"article_images/article_{i+1}.jpg"  # Set the image path
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)  # Save the image to disk
                print(f"Image saved: {img_path}")
        else:
            print("No cover image found for article.")

        # Fetch full article content
        driver.get(link)
        article_content = ""

        try:
            # Check if the article contains a gallery-slider div
            if driver.find_elements(By.ID, "gallery-slider"):
                print("Gallery format detected. Extracting image captions.")
                figures = driver.find_elements(By.XPATH, "//div[@id='gallery-slider']//figure")
                captions = []

                for idx, fig in enumerate(figures):
                    try:
                        caption = driver.execute_script("return arguments[0].innerText;", fig.find_element(By.XPATH, ".//figcaption")).strip()
                        if caption:
                            captions.append(caption)
                        
                        # Save gallery images
                        img_element = fig.find_element(By.XPATH, ".//img")
                        img_url = img_element.get_attribute("src")
                        if img_url:
                            img_data = requests.get(img_url).content
                            img_path = f"article_content_images/article_{i+1}_img_{idx+1}.jpg"
                            with open(img_path, "wb") as img_file:
                                img_file.write(img_data)
                            print(f"Gallery Image saved: {img_path}")
                    except Exception as e:
                        print(f"Error saving gallery image {idx+1}: {e}")
                        continue
                
                article_content = "\n".join(captions) if captions else "No captions found."
            else:
                # Wait for the first paragraph to appear
                wait.until(EC.presence_of_element_located((By.XPATH, "//article//p")))

                # Scroll to load all content
                last_height = driver.execute_script("return document.body.scrollHeight")
                max_attempts = 15  # Increase max scroll attempts
                attempt = 0

                while attempt < max_attempts:
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    time.sleep(1)  # Reduce sleep time for better efficiency

                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:  # Stop when no new content loads
                        break
                    last_height = new_height
                    attempt += 1

                # ** Extract all <p> tags using JS to ensure full content extraction **
                article_content = driver.execute_script("""
                    let paragraphs = document.querySelectorAll('article p, div.article p, section p');
                    return Array.from(paragraphs).map(p => p.innerText).join('\\n');
                """)

                # Handle paywalls or missing content
                if not article_content.strip():
                    paywall_check = driver.find_elements(By.XPATH, "//span[@name='elpais_ico']")
                    if paywall_check:
                        article_content = "This article requires a subscription."

        except Exception:
            article_content = "No content available."
  
        # Print results
        print(f"\nArticle {i+1}:")
        print(f"Title (Spanish): {title}")
        print(f"Title (English): {translated_title}")
        print(f"Link: {link}")
        print(f"Summary: {summary}")
        print(f"Content (Spanish):\n{article_content}\n")

        # Navigate back to the Opinion section. This could be optimized in the future, as 'driver.back()' 
        # may cause unnecessary page reloads. A more efficient approach could involve direct DOM interaction.      
        driver.back()
        wait.until(EC.presence_of_element_located((By.XPATH, "//article")))
        time.sleep(1) 

    except Exception as e:
        print(f"Error processing article {i+1}: {e}")

# Step 4: Word frequency analysis
# Define a simple set of stopwords
stopwords_set = {"the", "of", "in", "and", "a", "to", "for", "on", "at", "with", "by", "is", "as", "an"}

word_counts = Counter()
for title in translated_titles:
    words = re.findall(r"\b\w+\b", title.lower())  
    word_counts.update(word for word in words if word not in stopwords_set)

# Filter words that appear more than twice
repeated_words = {word: count for word, count in word_counts.items() if count > 2}

# Print results
print("\nWord Frequency Analysis:")
if repeated_words:
    for word, count in repeated_words.items():
        print(f"{word}: {count}")
else:
    print("No words are repeated more than twice.")

# Close browser
driver.quit()
