#NAME: W.D.S.R.RUDRIGO
#INDEX : 21/ENG/151

import random
import nltk
import  re
import string
from fuzzywuzzy import process
from colorama import Fore, Style, init
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import warnings

init(autoreset=True)

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

# Initialize WordNetLemmatizer and stopwords
lemmatizer = nltk.stem.WordNetLemmatizer()
stopwords = set(nltk.corpus.stopwords.words('english'))

# Function to load goods locations from file
def load_goods_locations(filename):
    goods_db = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    good, location = line.split(':')
                    goods_db[good.strip()] = location.strip()
                except ValueError:
                    continue
    return goods_db

goods_db = load_goods_locations('data.txt')
goods_set = set(goods_db.keys())

# Function to provide the location of each good
def get_shelf_location(good):
    return goods_db.get(good.lower(), "Sorry, I don't know where that is.")

# Function to save the locations to a file
def save_locations_to_file(locations, customer_name):
    filename = f"{customer_name}_shelf_locations.txt"
    with open(filename, 'w') as f:
        f.write(f"Customer: {customer_name}\n\n")
        for good, location in locations.items():
            f.write(f"{good.capitalize()}: {location}\n")
    print(Fore.GREEN + f"Locations saved to {filename}")
    return filename

def clear_console_simulation():
    print("\n" * 100)

# Function to preprocess text
def preprocess_text(text):
    words = nltk.word_tokenize(text)
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word.isalnum() and word.lower() not in stopwords]
    return words

# Function to handle greetings
def greet(sentence):
    greet_inputs = ('hello', 'hi', 'hey', 'greetings')
    greet_responses = ('Hi there!', 'Hello!', 'Hey! How can I assist you today?')
    for word in sentence.lower().split():
        if word in greet_inputs:
            return random.choice(greet_responses)
    return None

# Function to find the closest match for a word in goods_set
def find_best_match(word):
    match, score = process.extractOne(word, goods_set)
    return match if score > 70 else None

# Function to display a colorful header
def print_header():
    print(Fore.CYAN + Style.BRIGHT + "\nWelcome to the ABC Supermarket Assistant!🤖\n")
    print(Style.RESET_ALL + "-" * 50 + "\n")

# Function to print user-friendly instructions
def print_instructions():
    print(Fore.MAGENTA + "Instructions:")
    print("1. Enter the items you want to buy.")
    print("2. The bot will help you find their locations.")
    print("3. Type 'bye' or 'exit' to end the conversation.\n")

def is_valid_email(email):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False
# Function to send email with the locations file
def send_email(to_email, filename, customer_name):
    from_email = "abcsuppermarket924@gmail.com"
    password = "ayev zcng soeq ooxo"

    while True:
        if is_valid_email(to_email):
            break
        elif to_email.lower() in ['exit', 'bye']:
            print(Fore.BLUE + "🤖 Bot: Exiting email sending process.")
            return
        else:
            print(Fore.RED + "🤖 Bot: Invalid email address. Please enter a valid email address.")
            print(Fore.BLUE + "🤖 Bot: Please enter your email address.")
            to_email = input(Fore.YELLOW + "You: ").strip()

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"{customer_name}'s Shelf Locations"
    body = f"Hi {customer_name},\n\nPlease find the shelf locations of your items attached.\n\nBest regards,\nABC Supermarket Assistant"

    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")

    msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(Fore.GREEN + f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(Fore.RED + "🤖 Bot: Error sending email. Please check your credentials.")
        print(e)

# Main chatbot function
def supermarket_chatbot():
    print_header()
    print_instructions()

    print(Fore.BLUE + "🤖 Bot: Hello! What's your name?")

    customer_name = input(Fore.YELLOW + "You: ").strip()
    if customer_name.lower() in ['bye', 'exit']:
        print(Fore.BLUE + "🤖 Bot: Goodbye! Have a nice day!Come Agin!😊")

        return supermarket_chatbot()

    print(Fore.BLUE + f"🤖 Bot: Hello, {customer_name}! Please tell me what you want to buy today.")
    locations = {}

    while True:
        user_input = input(Fore.YELLOW + "You: ").strip().lower()

        if user_input.lower() in ['bye', 'exit']:
            print(Fore.BLUE + "🤖 Bot: Goodbye! Have a nice day!Come Agin!😊")
            filename = save_locations_to_file(locations, customer_name)
            return supermarket_chatbot()

        processed_goods = preprocess_text(user_input)
        response_messages = []

        for word in processed_goods:
            match = find_best_match(word)
            if match:
                location = get_shelf_location(match)
                locations[match] = location
                response_messages.append(
                    f"{Fore.GREEN}{match.capitalize()}{Style.RESET_ALL} is located at {Fore.YELLOW}{location}{Style.RESET_ALL}.")

        if locations:
            print(Fore.BLUE + "🤖 Bot: " + " ".join(response_messages))
        else:
            print(Fore.RED + "🤖 Bot: Sorry, I couldn't identify any valid items to locate.")

        print(Fore.BLUE + "🤖 Bot: Do you want to buy another thing? (yes/no)")
        more_items = input(Fore.YELLOW + "You: ").strip().lower()
        if more_items.lower() in ['bye', 'exit']:
            print(Fore.BLUE + "🤖 Bot: Goodbye! Have a nice day!Come Agin!😊")
            filename = save_locations_to_file(locations, customer_name)
            return supermarket_chatbot()

        if more_items == 'no':
            print(Fore.BLUE + f"🤖 Bot: Okay, {customer_name}, thank you very much!")
            filename = save_locations_to_file(locations, customer_name)
            locations.clear()

            # Ask for email and send the file
            print(Fore.BLUE + "🤖 Bot: Would you like to receive the locations file via email? (yes/no)")
            send_email_option = input(Fore.YELLOW + "You: ").strip().lower()

            if send_email_option == 'yes':
                print(Fore.BLUE + "🤖 Bot: Please enter your email address.")
                email_address = input(Fore.YELLOW + "You: ").strip()
                send_email(email_address, filename, customer_name)
            print(Fore.BLUE + "🤖 Bot: Goodbye! Have a nice day!Come Agin!😊")
            print(Fore.BLUE + "🤖 Bot: Press 'Enter' to clear chat history and start for a new customer...")
            input()
            clear_console_simulation()

            print(Fore.BLUE + "🤖 Bot: Starting a new session for the next customer...\n")
            return supermarket_chatbot()  # Restart the chatbot
        elif more_items == 'yes':
            print(Fore.BLUE + f"🤖 Bot: Please tell me what else you want to buy, {customer_name}.")

supermarket_chatbot()
