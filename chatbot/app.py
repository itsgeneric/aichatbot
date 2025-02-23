'''
Program Author: Anirudh R

This project attempts to solve the problem statement with a basic chatbot that understands and interprets any website
provided to it. A SQLite 3 Database has been connected so that everytime the user enters a URL, it is logged into the
database and is automatically deleted in 24 hours due time. Within the 24 hours, if the user enters the same website
again, the database triggers a response where it asks the user if they want to connect to a sales representative.

The above functionalities are achieved by using Flask, BeautifulSoup, SQLite and a simple HTML file that accompanies
this project that is responsible for basic frontend. Although it may not be perfect, I hope these functionalities meet
the requirements mentioned in the problem statement. The data is kept dynamic and all the data except the URL entered
gets automatically deleted when the user enters "exit" hence satisfying the requirement of not having permanent storage.

Date: 23 February 2025.
'''


from flask import Flask, render_template, request, jsonify  #Flask to render frontend
import requests #Requests to retrieve HTML content from the given URL
from bs4 import BeautifulSoup #Parsing the Website Contents giving access to functions like find, findall etc.
import re #To implement Regular Expressions in order to tokenise text. NLTK can be an alternative to this.
import sqlite3 #To support the URL Database to implement the 24-hour rule as mentioned in the question.
from datetime import datetime, timedelta #Keep track of time.

app = Flask(__name__)
website_data = {}
CHATBOT_DB = 'chatbot.db'

#In the following functions, I have seperated each SQL Query into one function for simplicity.
#We create a database titled chatbot using SQLite Data Source and initialise it. (for first run)
def init_db():
    with sqlite3.connect(CHATBOT_DB) as conn:
        cursor = conn.cursor() #Creating a cursor to execute the query
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS url (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''') #The table consists of id, URL, and a timestamp to track 24 hours.
        conn.commit() #This command saves the changes into the database.

# If the timestamp when subtracted returns under 24 hours, it is a returning URL.
def returning_url(url):
    with sqlite3.connect(CHATBOT_DB) as conn:
        cursor = conn.cursor()
        #We should now retrieve the URL's timestamp
        cursor.execute("SELECT timestamp FROM url WHERE url = ?", (url,))
        result = cursor.fetchone()
        if result:
            #Converts the timestamp into readable YY MM DD HH MM SS format which we can use to check if its under 24 hours
            time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            return datetime.now() - time < timedelta(hours=24)
    #Returns the time difference if it is within 24 hours, else returns False.
    return False

# Insert urls into the table.
def insert(url):
    with sqlite3.connect(CHATBOT_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO url (url) VALUES (?)", (url,))
        conn.commit() #Save changes into the database.

# Function that attempts to remove entries that are older than 24 hours using the timestamp
def remove():
    with sqlite3.connect(CHATBOT_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM url WHERE timestamp < datetime('now', '-24 hours')")
        conn.commit()

# Not all inputs needs to be entered into the database to provide for privacy as mentioned in the question.
# Hence, we shall determine that URLs are those that start with http:// or https:// and identify them.
def is_url(text):
    return text.lower().startswith(('http://', 'https://'))

''' Elaborate keyword database with 60 words per category to identify the probable category of a given website.
These keywords are manually written after considering home pages of several test websites.
Weights are added to these keywords to avoid conflicts in case the same words are found.
Current time complexity is O(n) am constantly looking forward to implementing this with O(logn) complexity.
'''

KEYWORDS = {
    "shopping": {
        "buy": 2, "shop": 2, "cart": 2, "wishlist": 2, "price": 2, "product": 2, "sale": 2, "discount": 2, "order": 2, "checkout": 2,
        "purchase": 2, "deal": 2, "shipping": 1, "payment": 1, "delivery": 1, "basket": 2, "offer": 2, "promo": 2, "coupon": 2, "refund": 1,
        "return": 1, "stock": 1, "inventory": 1, "brand": 1, "review": 1, "rating": 1, "gift": 1, "card": 1, "track": 1, "ship": 1,
        "store": 2, "mall": 2, "market": 2, "ecommerce": 2, "online": 2, "retail": 2, "wholesale": 1, "auction": 1, "bid": 1, "win": 1,
        "clearance": 1, "outlet": 1, "flash": 1, "daily": 1, "exclusive": 1, "limited": 1, "preorder": 1, "subscription": 1, "membership": 1,
        "loyalty": 1, "points": 1, "reward": 1, "cashback": 1, "installment": 1, "finance": 1, "credit": 1, "debit": 1, "wallet": 1
    },
    "travel": {
        "flight": 2, "hotel": 2, "booking": 2, "reservation": 2, "trip": 2, "vacation": 2, "tour": 2, "destination": 2, "travel": 2,
        "airline": 2, "ticket": 2, "luggage": 1, "itinerary": 1, "cruise": 1, "resort": 1, "beach": 1, "adventure": 1, "safari": 1, "hiking": 1,
        "backpack": 1, "visa": 1, "passport": 1, "airport": 1, "terminal": 1, "boarding": 1, "checkin": 1, "checkout": 1, "cabin": 1, "suite": 1,
        "hostel": 1, "motel": 1, "inn": 1, "lodging": 1, "accommodation": 1, "car rental": 1, "transport": 1, "transfer": 1, "guide": 1, "sightseeing": 1,
        "attraction": 1, "landmark": 1, "culture": 1, "cuisine": 1, "local": 1, "international": 1, "domestic": 1, "budget": 1, "luxury": 1,
        "package": 1, "deal": 1, "discount": 1, "promo": 1, "offer": 1, "last minute": 1, "seasonal": 1, "holiday": 1, "festival": 1, "event": 1, "experience": 1
    },
    "information": {
        "about": 2, "contact": 2, "faq": 2, "help": 2, "support": 2, "blog": 2, "news": 2, "article": 2, "post": 2, "read": 2,
        "guide": 1, "resource": 1, "documentation": 1, "manual": 1, "tutorial": 1, "howto": 1, "instruction": 1, "step": 1, "tip": 1, "advice": 1,
        "knowledge": 1, "library": 1, "archive": 1, "history": 1, "fact": 1, "statistic": 1, "data": 1, "research": 1, "study": 1, "analysis": 1,
        "report": 1, "white paper": 1, "case study": 1, "survey": 1, "poll": 1, "interview": 1, "review": 1, "rating": 1, "feedback": 1, "comment": 1,
        "forum": 1, "discussion": 1, "community": 1, "q&a": 1, "question": 1, "answer": 1, "explanation": 1, "definition": 1, "meaning": 1, "example": 1
    },
    "social media": {
        "profile": 2, "timeline": 2, "feed": 2, "post": 2, "share": 2, "like": 2, "comment": 2, "follow": 2, "follower": 2, "hashtag": 2,
        "instagram": 2, "facebook": 2, "whatsapp": 2, "reddit": 2, "twitter": 2, "Log in": 2, "Sign up": 2, "message": 1, "chat": 1, "group": 1,
        "community": 1, "network": 1, "connection": 1, "friend": 1, "following": 1, "story": 1, "reel": 1, "live": 1, "stream": 1,
        "video": 1, "photo": 1, "image": 1, "album": 1, "gallery": 1, "filter": 1, "effect": 1, "trend": 1, "viral": 1, "meme": 1,
        "emoji": 1, "sticker": 1, "gif": 1, "poll": 1, "quiz": 1, "event": 1, "notification": 1, "alert": 1, "update": 1, "newsfeed": 1
    },
    "entertainment": {
        "movie": 2, "film": 2, "tv": 2, "show": 2, "series": 2, "episode": 2, "stream": 2, "watch": 2, "listen": 2, "music": 2,
        "concert": 1, "theater": 1, "game": 1, "play": 1, "video": 1, "song": 1, "album": 1, "artist": 1, "band": 1, "genre": 1,
        "comedy": 1, "drama": 1, "action": 1, "horror": 1, "romance": 1, "sci-fi": 1, "fantasy": 1, "animation": 1, "documentary": 1, "trailer": 1,
        "premiere": 1, "release": 1, "download": 1, "upload": 1, "subscribe": 1, "channel": 1, "playlist": 1, "podcast": 1, "radio": 1, "live": 1,
        "ticket": 1, "event": 1, "festival": 1, "award": 1, "nomination": 1, "celebrity": 1, "actor": 1, "actress": 1, "director": 1, "producer": 1
    },
    "finance": {
        "bank": 2, "account": 2, "loan": 2, "credit": 2, "debit": 2, "card": 2, "payment": 2, "transfer": 2, "withdrawal": 2, "deposit": 2,
        "interest": 1, "mortgage": 1, "investment": 1, "stock": 1, "insurance": 1, "tax": 1, "refund": 1, "budget": 1, "expense": 1, "income": 1,
        "salary": 1, "wage": 1, "bonus": 1, "dividend": 1, "profit": 1, "loss": 1, "revenue": 1, "expenditure": 1, "savings": 1, "retirement": 1,
        "pension": 1, "forex": 1, "currency": 1, "exchange": 1, "rate": 1, "crypto": 1, "bitcoin": 1, "ethereum": 1, "wallet": 1, "blockchain": 1,
        "trading": 1, "broker": 1, "portfolio": 1, "asset": 1, "liability": 1, "equity": 1, "debt": 1, "credit score": 1, "report": 1, "statement": 1
    }
}

'''We have to now simulate a client environment to fetch the website contents.
Some sophisticated websites like Amazon, often return bad status codes or ask for a captcha when a bot tries to 
access the website. Hence, we implement a try-catch block to handle the same so that it does not crash the program. '''

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 Chrome/91.0.4472.124 Safari/537.36"
    } #Headers define what needs to be sent with the request in order to identify the client.
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        return response.text
    except requests.RequestException as e: #In case a bad exception is thrown. (Amazon.com threw 503 during test cases)
        return None

# Parsing the HTML content into a BeautifulSoup object (DOM) so that it can now be queried easily.
def parse(html_content):
    return BeautifulSoup(html_content, 'html.parser')

# Now that the website's HTML is successfully parsed, we can query it for various information.
# First, we query it for the title which is usually the title tag in an HTML file.
def get_title(soup):
    title = soup.find('title')
    return title.get_text().strip() if title else "This website has no title."

# Now, we query website headings. In an HTML file, headings are usually h1, h2, h3, h4, h5 or h6 tags.
def get_headings(soup):
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return [heading.get_text().strip() for heading in headings]

# We can now extract all the 'a href' tags to get all the website links
def get_links(soup):
    links = soup.find_all('a', href=True)
    return [link['href'] for link in links]

# A simple function to calculate the word count using the length of the get_text function
# Alternatively, we can also use this function to just display the website text.
def word_count(soup):
    text = soup.get_text()
    words = text.split()
    return len(words)

''' The generated data now needs to be tokenised into words so that we can search through them later to find the 
category of the website. To tokenise them, we must keep in mind that all text must be converted to lower and must be 
stripped of punctuations. So, it has to be a sequence of word characters surrounded by boundaries on both sides. '''
def tokenize_text(text):
    return re.findall(r'\b\w+\b', text.lower()) #Using Regex to tokenise the text into meaningful words

# Now for the website description, we can use the tokenised words to predict the category it belongs to.
def describe(soup):
    text = soup.get_text().lower()
    tokens = tokenize_text(text)

    # Have to calculate the scores for each category and then predict which category it might belong to.
    category_scores = {category: 0 for category in KEYWORDS.keys()} #Dictionary for scores
    matched_keywords = {category: set() for category in KEYWORDS.keys()} #Dictionary to store the matched keywords

    # Loop through KEYWORDS dictionary and update our category scores and matched keywords scores accordingly.
    for category, keywords in KEYWORDS.items():
        for token in tokens:
            if token in keywords:
                category_scores[category] += keywords[token]
                matched_keywords[category].add(token)

    # The category with the highest score is highly likely to be the actual category of the website.
    if category_scores:
        purpose = max(category_scores, key=category_scores.get)
    else:
        purpose = "information"  # Default category since all websites display some form of information.

    # Meaningful sentences as response corresponding to each category.
    if purpose == "shopping":
        description = "This website is a shopping platform. You can buy the products that you like from here.\n"
    elif purpose == "travel":
        description = "This website is a travel platform. You can buy travel tickets or get information about places you want to go from here.\n"
    elif purpose == "information":
        description = "This website provides meaningful information about something that can be seen in the keywords.\n"
    elif purpose == "social media":
        description = "This website is a social media platform where you can connect with other people.\n"
    elif purpose == "entertainment":
        description = "This website is an entertainment platform, typically used for recreational purposes.\n"
    elif purpose == "finance":
        description = "This website is a financial platform.\n"
    else:
        description = "This website provides meaningful information about something that can be seen in the keywords.\n"

    # The matched keywords shall also be shown as output in the chatbot for better understanding from the user side.
    matched_keywords_list = matched_keywords[purpose]
    if matched_keywords_list:
        description += f"\nMatched Keywords: {', '.join(matched_keywords_list)}"
    else:
        description += "\nNo keywords matched."

    return description

# Soup can also extract meta tags, scripts, stylesheets etc. that can be found in their corresponding html tags.
# We shall display them as technical details of the website.
def describe_technical(soup):
    meta_tags = soup.find_all('meta')
    scripts = soup.find_all('script')
    stylesheets = soup.find_all('link', rel='stylesheet')

    technical_description = "Technical details about the website:\n"
    technical_description += f"- Meta Tags: {len(meta_tags)} meta tags are present, including descriptions, keywords, and viewport settings.\n"
    technical_description += f"- Scripts: {len(scripts)} scripts are used for interactivity and dynamic content.\n"
    technical_description += f"- Stylesheets: {len(stylesheets)} stylesheets are used for styling the website.\n"
    return technical_description

'''Now that the main functionality is complete, the focus is shifted to frontend. Flask is used to pass data into 
index.html which is located inside the 'templates' directory of this project.'''

# First job is to render the HTML file. home() function for the root URL which in our case is a localhost port.
@app.route("/")
def home():
    return render_template("index.html")

# All POST requests to the /ask endpoint.
@app.route("/ask", methods=["POST"])

#Let ask be the main function. The chat is active as long as this function is running. This function handles the POST
# requests to the /ask endpoint.

def ask():
    user_input = request.json.get("input").strip().lower() #Extracts user input (text)
    if user_input == "exit":
        website_data.clear() #Clears data in order to maintain privacy.
        return jsonify({"response": "Goodbye! You can leave or start over by entering a new URL."})

    # Check if the input is a URL
    if is_url(user_input):
        # Remove any entries that are over 24 hours old.
        remove()
        # Check if this is a "Follow - up" i.e. returning within 24 hours.
        returning_user = returning_url(user_input)
        insert(user_input) #Inserting URL into the chatbot.db

        # Fetch and parse website content at the given URL by the user.
        html_content = fetch(user_input)
        if not html_content:
            website_data.clear()
            return jsonify({"response": "Error fetching the website. This is either due to blocked access or invalid URL. Please try again."})
        website_data["soup"] = parse(html_content) #parse the website data with key soup and store it into a dictionary

        # Implementing the follow-up system for CRM.
        if returning_user:
            website_data["returning_user"] = True  # flag for returning users
            return jsonify({"response": "We see you have visited this site more than once in the last 24 hours... Do you want to connect to a sales representative? (yes/no)"})
        else:
            # Process queries after setting the flag to false in case its a new user.
            website_data["returning_user"] = False  # Reset the flag
            return jsonify({"response": "Ask me anything about the website."})
    else:
        # Invalid URL
        if "soup" not in website_data:
            return jsonify({"response": "Please enter a valid URL."})

        # Store all the values of the key soup from the dictionary website_data into soup.
        soup = website_data["soup"]
        # Corresponding sales representative prompt for returning users has been implemented below:
        if website_data.get("returning_user", False):
            if user_input == "yes":
                website_data["returning_user"] = False  # Reset the flag
                return jsonify({"response": "Please call our sales representative at +1-800-123-4567."})
            elif user_input == "no":
                website_data["returning_user"] = False  # Reset the flag
                return jsonify({})  # Respond with nothing when they say no
            else:
                pass

        # The functions previously defined are called in their corresponding cases below and are then passed as responses.

        # Title, heading, links, word count, website description, technical description and exit functionalities are implemented below.
        if "title" in user_input:
            response = f"Website Title: {get_title(soup)}."
        elif "heading" in user_input:
            headings = get_headings(soup)
            if headings:
                response = "Website Headings :\n- " + "\n- ".join(headings)
            else:
                response = "There are no headings associated with this website."
        elif "link" in user_input:
            links = get_links(soup)
            if links:
                response = "Website Links:\n- " + "\n- ".join(links)
            else:
                response = "There are no links associated with this website."
        elif "word" in user_input and "count" in user_input:
            words = word_count(soup)
            response = f"The website has approximately {words} words."
        elif "describe" in user_input and "website" in user_input:
            response = describe(soup)
        elif "describe" in user_input and "technical" in user_input:
            response = describe_technical(soup)
        else:
            response = "I'm not capable of answering this yet. \n You can ask something about the website's title, headings, links, word count, or ask me to describe the website or its technical details."

        return jsonify({"response": response}) # Return the response according to the user input.
    
if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True) # Run the web server for the application