import requests
import time
from recipe_scrapers import scrape_me as recipe_scraper
from bs4 import BeautifulSoup
import pymongo
import uuid
import mimetypes
import config

# starts the database
client = pymongo.MongoClient(config.mongodb_url)
db = client["Recipeze"]
col = db["recipes"]


def generate_ID():
    return uuid.uuid4().hex.upper()[0:6]


def save_img(img_url, recipeID):
    """ saves image to the file path in the config file, used to retrieve from DB """
    img_response = requests.get(img_url)
    content_type = img_response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    img_path = f"{config.img_file_path}/{recipeID}{extension}"
    with open(img_path, "wb") as f:
        f.write(img_response.content)
    return img_path


def save_recipe(recipe_data):
    """ converts the parsed recipe from the library to a format we can save to the DB """
    title = recipe_data.title()
    # we don't want duplicate recipes being imported
    if col.count_documents({"title": title}) == 0:
        recipeID = generateID()
        while col.count_documents({"_id": recipeID}) > 0:
            recipeID = generateID()
        instructions = [
            x for x in recipe_data.instructions().split("\n") if x != ""]
        ingredients = recipe_data.ingredients()
        time = recipe_data.total_time()
        amount = recipe_data.yields()
        img_path = save_img(recipe_data.image(), recipeID)
        payload = {"_id": recipeID, "title": title, "time": time, "ingredients": ingredients,
                   "instructions": instructions, "image": img_path, "amount": amount}
        col.insert_one(payload)
        print(f"Processed {title}")


def init(page_count):
    """ scrapes allrecipes.com for recipes from page_count page, first page has 29 recipes, the restare 20 recipes per page"""
    count = 0
    recipe_urls = []
    # goes through each page on the site and gathers links to the recipe for our library to use
    for i in range(1, page_count):
        req = requests.get(f"https://www.allrecipes.com/recipes/?page={i}")
        soup = BeautifulSoup(req.content, 'html.parser')
        links = soup.findAll("a", {"class": "fixed-recipe-card__title-link"})
        for link in links:
            recipe_urls.append(link["href"])
            count += 1
        print(f"Captured {count} recipes so far")

    print(f"Processing {count} recipes")

    for recipe in recipe_urls:
        recipe_data = recipe_scraper(recipe)
        save_recipe(recipe_data)

#starts the process
init(101)