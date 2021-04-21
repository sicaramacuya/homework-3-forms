from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
import json
import os
import random
import requests
# from dotenv import load_dotenv
# load_dotenv()

secret_key = os.getenv('SECRET_KEY')
print(secret_key)

app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""

    num_compliments = int(request.args.get('num_compliments'))

    context = {
        'users_name': request.args.get('users_name'),
        'wants_compliments': request.args.get('wants_compliments'),
        'compliments': random.sample(list_of_compliments, k=num_compliments)
    }

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.',
    'pistol shrimp': 'The Pistol Shrimp is capable of snapping it’s claw shut so rapidly, that it creates a bubble which collapses to produce a sonic blast.',
    'otters': 'Otters “hold hands” while sleeping, so they don’t float away from each other.',
    'hummingbirds': 'Hummingbirds are the only known birds that can also fly backwards.',
    'dolphins': 'Dolphins use toxic pufferfish to \'get high\'.'
}

place_holder = {
    'fact_here': 'Your animal fact goes here.'
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    animal_name = request.args.get('animal')

    if animal_name is None:

        context = {
        'animal_list_keys': animal_to_fact.keys(), 
        'animal_fact': place_holder['fact_here']
        }
        return render_template('animal_facts.html', **context)

    context = {
        'animal_list_keys': animal_to_fact.keys(), 
        'animal_fact': animal_to_fact[animal_name]
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""

    if request.method == 'POST':
        
        filter_type = request.form.get('filter_type')
        
        image = request.files.get('users_image')

        new_file_path = save_image(image, filter_type)

        apply_filter(new_file_path, filter_type)

        image_url = f'/static/images/{image.filename}'

        context = {
            'filter_types_keys': filter_types_dict.keys(),
            'image_url': image_url
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            'filter_types_keys': filter_types_dict.keys(),
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = 'LIVDSRZULELA'
TENOR_URL = 'https://api.tenor.com/v1/search'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        quantity_gifts = request.form.get('quantity')

        response = requests.get(
            TENOR_URL,
            {
                'q': search_query,
                'key': API_KEY,
                'limit': quantity_gifts
            })

        gifs = json.loads(response.content).get('results')

        gifts_urls = []
        for num in range(int(quantity_gifts)):
            gifts_urls.append(gifs[num]['media'][0]['gif']['url'])

        context = {
            'gifs': gifs,
            'gifts_urls': gifts_urls
        }

        # Uncomment me to see the result JSON!
        # pp.pprint(gifs)

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)