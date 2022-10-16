import requests
import json
from bs4 import BeautifulSoup
import pandas as pd 
from concurrent.futures import ThreadPoolExecutor
import time
from tqdm.notebook import tqdm
from tqdm import tqdm as tqdm2
from tqdm.contrib.concurrent import thread_map


Total_Data = []
Product_Links = []
Category_Names = []
Category_Links = []

def get_data(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r , 'lxml')
    script = soup.find_all('script' , {'type':'application/ld+json'})[1].text
    jdata = json.loads(script)
    # Title
    title = jdata['name']
    # Description
    try:
        description_div = soup.find('div' , class_='js-item-description item-description')
        description = description_div.div.contents
        description = ''.join(map(str, description)).replace('’', "'")
        
    except:
        try:
            description = jdata['description']
        except:
            description = ''
    #### video and images
    # VIDEO LINK
    try:
        video_div = soup.find('div' , class_='video-preview-wrapper')
        video_link = video_div.a['href']
    except:
        video_link = ''
    # IMAGE LINK
    try:
        image_div = soup.find('div' , class_='video-preview-wrapper')
        image_link = image_div.img['src']
    except:
        image_link = ''

    
    data = {
        'Product Title': title,
        'Product Link': url,
        'Description': description,
        'Image Preview Link': image_link,
        'Video Preview Link': video_link
    }
    Total_Data.append(data)
    return

def category():
    url = 'https://videohive.net/category'
    r = requests.get(url).text
    soup = BeautifulSoup(r , 'lxml')
    ul = soup.find('ul' , class_='first')
    atags = soup.find_all('a' , class_='off-canvas-category-link')
    for i in range(1 , len(atags)-2):
        cat_name = atags[i].text.strip()
        cat_link = 'https://videohive.net/' + atags[i]['href']
        Category_Names.append(cat_name)
        Category_Links.append(cat_link)
    return

def getProds(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r , 'lxml')
    atags = soup.select('.shared-item_cards-item_name_component__itemNameLink')
    for i in atags:
        prod_link = i['href']
        Product_Links.append(prod_link)
    return



print('\nHow do you want to scrape?')
print('\n')
print('1: Category Wise')
print('2: Link Wise')
print('\n')
num = int(input('Enter Number: '))
print('\n')

if num == 1:
    category()
    for i in range(len(Category_Names)):
        print(f'{i+1}: {Category_Names[i]}')
    
    print('\nWhich category do you want to scrape?')
    print('\n')
    n = int(input(f'Enter a Number from 1 to {len(Category_Names)}: '))
    print('\n')
    p = int(input('How many products do you want to scrape? '))
    L = (p//30)+1    
    # Getting the category link
    print('Fetching the Product Links')
    for x in range(1 , L+1):
        link_index = Category_Links[n-1] + f'?page={x}&sort=date#content'
        getProds(link_index)
    
    actual_Products = Product_Links[0:p]
    # getting Total Data
    print('\n')
    print('Fetching Products Data')
    thread_map(get_data , actual_Products , max_workers=10)
    df = pd.DataFrame(Total_Data)
    file_name = f'{Category_Names[n-1]}.csv'
    df.to_csv(file_name , index=False)
    print('\nData Stored to CSV')
    time.sleep(3)

elif num==2:
    LINK = input('Enter the Product Link: ')
    r = requests.get(LINK).text
    soup = BeautifulSoup(r , 'lxml')
    script = soup.find_all('script' , {'type':'application/ld+json'})[1].text
    jdata = json.loads(script)
    # Title
    title = jdata['name'].strip()
    filename = f"{title}.csv"
    get_data(LINK)
    df = pd.DataFrame(Total_Data)
    df.to_csv(filename , index=False)
    print('\nData Stored to CSV')
    time.sleep(3)

else:
    print('Incorrect Entry....')