from flask import Flask, render_template, request, redirect, url_for
import os
import openai
from dotenv import load_dotenv
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Blueprint, render_template

app = Flask(__name__)

# Load the .env file
load_dotenv()

# Get the OpenAI key from the environment variables
openai.api_key = os.getenv('OPENAI_KEY')

gdn_bp = Blueprint('gdn', __name__)

@gdn_bp.route('/gdn', methods=['GET', 'POST'])
def gdn():
    return render_template('gdn.html')

# Define the lists of engagement formats and emotional triggers
engagement_formats = [
    'Call to Action',
    'Clickbait',
    'Innovation Driving Cost Benefit',
    'Missed Opportunity Awareness',
    'Offer Announcement + Call to Action',
    'Offer Announcement + Inclusivity',
    'Price Discovery',
    'Prices May Surprise You',
    'Problem Statement + Solution',
    'Provocative Questioning',
    'Question',
    'Question + Call to Action',
    'Question + Problem Statement + Solution',
    'Question + Solution',
    'Search Call to Action',
    'Statement',
    'Statement + Call to Action',
    'Statement + Expectation Challenge',
    'Statement Regarding Health Symptoms',
    'Statistics Based',
    'Topic Introduction',
    'Offer Announcement + Exclusivity',
    'Fear of Missing Out',
    'Tactics to Try Tonight',
    'Question + Urgency',
    'Question + Offer',
    'How To',
    'How To + Treatments',
    'Seniors Have Been Experiencing',
    'List of Symptoms',
    'Deals'
]

emotional_triggers = [
    'Adventure',
    'Affinity',
    'Affordability',
    'Ambition',
    'Anger',
    'Anticipation',
    'Convenience',
    'Cost Sensitivity',
    'Curiosity',
    'Danger',
    'Discovery',
    'Easy Accessibility',
    'Empowerment',
    'Envy',
    'Fear of Ignoring Health Symptoms',
    'Fear of Missing Information',
    'Fear of Missing Out',
    'Fear of Old Age',
    'Fear of Potential Health Issue',
    'Financial Gain',
    'Greed',
    'Hope',
    'Hop and Affordability',
    'Improve Compensation Level',
    'Improve Financial Situation',
    'Improve Quality of Life',
    'Localization',
    'Love',
    'Nostalgia',
    'Not Too Late',
    'Opportunity',
    'Optimism',
    'Relief',
    'Savings',
    'Scarcity',
    'Security',
    'Surprise',
    'Timeliness',
    'Transparency',
    'Trust',
    'Urgency',
    'Validation',
    'Vanity'
]

tone = [
    'Happy',
    'Excited',
    'Sad',
    'Anxious',
    'Calm',
    'Passionate',
    'Serious',
    'Humorous',
    'Ironic',
    'Inspiring',
    'Empathetic',
    'Formal',
    'Casual',
    'Optimistic',
    'Pessimistic',
    'Fearful',
    'Nostalgic',
    'Affectionate',
    'Sympathetic',
    'Curious',
    'Energetic',
    'Indifferent',
    'Confident',
    'Surprised',
    'Angry',
    'Suspenseful',
    'Mysterious',
    'Hopeful',
    'Gloomy',
    'Skeptical'
]

# Use the service account credentials and gspread to access the Google Spreadsheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Spreadsheet by its key
spreadsheet = client.open_by_key("1eDGulXJxIoT-DMN2q6O7lR11hgCDXWGSLMyIRDj1D8Y")
sheet = spreadsheet.sheet1  # Access sheet 1

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user']  # Get the selected user
        engagement_format = request.form['engagement_format']  # Get the selected engagement format
        emotional_trigger = request.form['emotional_trigger']  # Get the selected emotional trigger
        topic = request.form['topic']  # Get the topic
        tone = request.form['tone']  # Get the selected tone

        sheet = None
        if user_input.lower() == 'matt':
            sheet = spreadsheet.get_worksheet(1)  # Access sheet 2
        elif user_input.lower() == 'january':
            sheet = spreadsheet.sheet1  # Access sheet 1
        else:
            return "Invalid sheet name."

        if engagement_format.lower() == 'random':
            engagement_format = random.choice(engagement_formats)

        if emotional_trigger.lower() == 'random':
            emotional_trigger = random.choice(emotional_triggers)

        if tone.lower() == 'random':  # Added this block for random tone selection
            tone = random.choice(tones)

        description = generate_headlines(sheet, topic, engagement_format, emotional_trigger, tone)
        return redirect(url_for('result', description=description))

    return render_template('index.html')



def generate_headlines(sheet, topic, engagement_format, emotional_trigger, tone):
    # Check if the header row exists
    if sheet.row_count == 0:
        # Append column headers to the sheet
        sheet.append_row(["Topic", "Engagement Format", "Emotional Trigger", "Tone", "Headline"])

    # Loop 3 times to create 3 different headlines
    for _ in range(3):
        if engagement_format.lower() == 'random':
            engagement_format = random.choice(engagement_formats)

        if emotional_trigger.lower() == 'random':
            emotional_trigger = random.choice(emotional_triggers)

        if tone.lower() == 'random':
            tone = random.choice(tone)

        # Define the prompt for the completion
        prompt = f"Create an ad headline for {topic} with the the tone {tone} and the following conditions:\n1. Engagement Format: {engagement_format}\n2. Emotional Trigger: {emotional_trigger}\n3. Tone: {tone}"

        # Use OpenAI's API to create the completion
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)

        # Add a prompt for GPT-3 to suggest an appropriate emoji for the headline
        emoji_prompt = f"What is an appropriate emoji to go with this headline: {response.choices[0].text.strip()}?"

        emoji_response = openai.Completion.create(engine="text-davinci-003", prompt=emoji_prompt, max_tokens=10)

        # Add the suggested emoji to the start of the headline
        headline = emoji_response.choices[0].text.strip() + " " + response.choices[0].text.strip()

        # Define the prompt for the description
        description_prompt = f"Describe the idea behind the topic {topic} in 30 words or less."

        # Use OpenAI's API to create the description
        description_response = openai.Completion.create(engine="text-davinci-003", prompt=description_prompt, max_tokens=60)

        # Get the suggested description and make sure it's 30 words or less
        description = ' '.join(description_response.choices[0].text.strip().split()[:30])

        # Add the data to the Google Spreadsheet
        sheet.append_row([topic, engagement_format, emotional_trigger, tone, headline, description])

    # Return the confirmation message
    return f"3 headlines about {topic} have been generated."



@app.route('/result')
def result():
    description = request.args.get('description')
    return render_template('index.html', description=description)

def get_recent_10(column_index):
    # Get all non-empty values from the specified column in the Google Spreadsheet
    values = sheet.col_values(column_index)[1:]
    # Remove empty values from the list
    values = [value for value in values if value.strip()]
    # Retrieve the recent 10 values
    recent_10_values = values[-10:]
    return recent_10_values

@app.route('/latest_topics')
def latest_topics():
    topics = get_recent_10(1)  # Retrieve the recent 10 topics
    topics = topics[::-1]  # Reverse the list to display from bottom to top

    # Retrieve the headlines for each topic
    headlines = get_recent_10(5)  # Get headlines
    headlines = headlines[::-1]  # Reverse the list to display from bottom to top

    # Retrieve the tone for each topic
    tones = get_recent_10(4)  # Get tones
    tones = tones[::-1]  # Reverse the list to display from bottom to top

    # Combine the topics, tones, and headlines into a list of tuples
    topic_tone_headlines = list(zip(topics, tones, headlines))

    return render_template('latest_topics.html', topic_tone_headlines=topic_tone_headlines)

@app.route('/gdn', methods=['GET', 'POST'])
def gdn():
    # You can add any logic you want to happen when the page is accessed here.
    return render_template('gdn.html')


if __name__ == '__main__':
    app.run(debug=True)


#One user
# from flask import Flask, render_template, request, redirect, url_for
# import os
# import openai
# from dotenv import load_dotenv
# import random
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# app = Flask(__name__)

# # Load the .env file
# load_dotenv()

# # Get the OpenAI key from the environment variables
# openai.api_key = os.getenv('OPENAI_KEY')

# # Define the lists of engagement formats and emotional triggers
# engagement_formats = [
#     'Call to Action',
#     'Clickbait',
#     'Innovation Driving Cost Benefit',
#     'Missed Opportunity Awareness',
#     'Offer Announcement + Call to Action',
#     'Offer Announcement + Inclusivity',
#     'Price Discovery',
#     'Prices May Surprise You',
#     'Problem Statement + Solution',
#     'Provocative Questioning',
#     'Question',
#     'Question + Call to Action',
#     'Question + Problem Statement + Solution',
#     'Question + Solution',
#     'Search Call to Action',
#     'Statement',
#     'Statement + Call to Action',
#     'Statement + Expectation Challenge',
#     'Statement Regarding Health Symptoms',
#     'Statistics Based',
#     'Topic Introduction',
#     'Offer Announcement + Exclusivity',
#     'Fear of Missing Out',
#     'Tactics to Try Tonight',
#     'Question + Urgency',
#     'Question + Offer',
#     'How To',
#     'How To + Treatments',
#     'Seniors Have Been Experiencing',
#     'List of Symptoms',
#     'Deals'
# ]

# emotional_triggers = [
#     'Adventure',
#     'Affinity',
#     'Affordability',
#     'Ambition',
#     'Anger',
#     'Anticipation',
#     'Convenience',
#     'Cost Sensitivity',
#     'Curiosity',
#     'Danger',
#     'Discovery',
#     'Easy Accessibility',
#     'Empowerment',
#     'Envy',
#     'Fear of Ignoring Health Symptoms',
#     'Fear of Missing Information',
#     'Fear of Missing Out',
#     'Fear of Old Age',
#     'Fear of Potential Health Issue',
#     'Financial Gain',
#     'Greed',
#     'Hope',
#     'Hop and Affordability',
#     'Improve Compensation Level',
#     'Improve Financial Situation',
#     'Improve Quality of Life',
#     'Localization',
#     'Love',
#     'Nostalgia',
#     'Not Too Late',
#     'Opportunity',
#     'Optimism',
#     'Relief',
#     'Savings',
#     'Scarcity',
#     'Security',
#     'Surprise',
#     'Timeliness',
#     'Transparency',
#     'Trust',
#     'Urgency',
#     'Validation',
#     'Vanity'
# ]

# # Use the service account credentials and gspread to access the Google Spreadsheet
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
# client = gspread.authorize(creds)

# # Open the Google Spreadsheet by its key
# spreadsheet = client.open_by_key("1eDGulXJxIoT-DMN2q6O7lR11hgCDXWGSLMyIRDj1D8Y")
# sheet = spreadsheet.sheet1  # Access sheet 1


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         user_input = request.form['topic']
#         description = generate_headlines(user_input)
#         last_10_topics = get_last_10_topics()
#         return redirect(url_for('result', description=description, last_10_topics=last_10_topics))

#     last_10_topics = get_last_10_topics()
#     return render_template('index.html', last_10_topics=last_10_topics)


# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         user_input = request.form['topic']
#         description = generate_headlines(user_input)
#         last_10_topics = get_last_10_topics()
#         return redirect(url_for('result', description=description, last_10_topics=','.join(last_10_topics)))

#     last_10_topics = get_last_10_topics()
#     return render_template('index.html', last_10_topics=last_10_topics)

# @app.route('/result')
# def result():
#     description = request.args.get('description')
#     last_10_topics = request.args.get('last_10_topics').split(',')
#     return render_template('index.html', description=description, last_10_topics=last_10_topics)


# def generate_headlines(topic):
#     # Check if the header row exists
#     if sheet.row_count == 0:
#         # Append column headers to the sheet
#         sheet.append_row(["Topic", "Engagement Format", "Emotional Trigger", "Headline"])

#     # Loop 1 time to create 1 different headline
#     for _ in range(3):
#         # Randomly choose an engagement format and an emotional trigger for each iteration
#         engagement_format = random.choice(engagement_formats)
#         emotional_trigger = random.choice(emotional_triggers)

#         # Define the prompt for the completion
#         prompt = f"Create an ad headline for {topic} with the following conditions:\n1. Engagement Format: {engagement_format}\n2. Emotional Trigger: {emotional_trigger}"

#         # Use OpenAI's API to create the completion
#         response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)

#         # Add a prompt for GPT-3 to suggest an appropriate emoji for the headline
#         emoji_prompt = f"What is an appropriate emoji to go with this headline: {response.choices[0].text.strip()}?"

#         emoji_response = openai.Completion.create(engine="text-davinci-003", prompt=emoji_prompt, max_tokens=10)

#         # Add the suggested emoji to the start of the headline
#         headline = emoji_response.choices[0].text.strip() + " " + response.choices[0].text.strip()

#         # Define the prompt for the description
#         description_prompt = f"Describe the idea behind the topic {topic} in 30 words or less."

#         # Use OpenAI's API to create the description
#         description_response = openai.Completion.create(engine="text-davinci-003", prompt=description_prompt, max_tokens=60)

#         # Get the suggested description and make sure it's 30 words or less
#         description = ' '.join(description_response.choices[0].text.strip().split()[:30])

#         # Add the data to the Google Spreadsheet
#         sheet.append_row([topic, engagement_format, emotional_trigger, headline, description])  # Added description

#     # Return the confirmation message
#     return f"3 headlines about {topic} have been generated."


# def get_last_10_topics():
#     # Get all non-empty topics from the Google Sheet
#     rows = sheet.get_all_records()
#     topics = [row['Topic'] for row in rows if row['Topic']]
#     # Retrieve the last 10 unique topics in reverse order
#     last_10_topics = list(reversed(topics[-10:]))
#     return last_10_topics



# if __name__ == '__main__':
#     app.run(debug=True)
