import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import os 
from . import config 

client = OpenAI(
    organization=config.ORGANIZATION_KEY, 
    api_key=config.OPENAI_KEY,
)

# currently unused
def check_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return link
        else:
            return redirect_to_wayback(link)
    except:
        return redirect_to_wayback(link)

# currently unused
def redirect_to_wayback(url):
    wayback_url = f"https://web.archive.org/web/*/{url}"
    return wayback_url

def process_data(url, question):
    if (url == "" or question == ""):
        return "Please enter a valid question and url"
    
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        context = []

        # makes sure that the user is only using wikipedia websites
        # 2 reasons, 1. the web scraper is setup for wikipedia, 2. The purpose of this project is to use wikipedia and return the links, not a budget chatgpt
        if "wikipedia" not in url:
            return "Please enter a valid Wikipedia URL"
        
        references = soup.find_all('ol', {'class' :'references'})

        for reference in references:
            links = reference.find_all('a', href=True)

        for link in links:
            if 'http' not in link['href']: # make sure that the link is an actual link (references in wikipedia are not always links)
                continue

            context.append(link['href'])

        messages = [{"role": "system", "content": content} for content in context]
        messages.append({"role": "system", 
                        "content": "Use only the previous links to answer any questions that you are given, if the links dont contain the answer then state 'No answer found', after answering the question, supply the link that you used to get the answer" 
        })

        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=100
        )

        return response.choices[0].message.content
    except Exception as e:
        return "Please enter a valid Wikipedia URL"
    finally: 
        pass
    
    