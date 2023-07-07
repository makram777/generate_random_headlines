from flask import Flask, render_template, request, redirect, url_for
import os
import openai
from dotenv import load_dotenv
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Load the .env file
load_dotenv()

# Get the OpenAI key from the environment variables
openai.api_key = os.getenv('OPENAI_KEY')

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

tones = [
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


def generate_headlines(sheet, topic, engagement_format, emotional_trigger, tone):
    # Define a dictionary to map engagement formats to emojis
    engagement_format_emojis = {
        'Call to Action': '📢',
        'Clickbait': '🔥',
        'Innovation Driving Cost Benefit': '💰',
        'Missed Opportunity Awareness': '⚠️',
        'Offer Announcement + Call to Action': '🎁',
        'Offer Announcement + Inclusivity': '🤝',
        'Price Discovery': '💲',
        'Prices May Surprise You': '😲',
        'Problem Statement + Solution': '🔍💡',
        'Provocative Questioning': '❓',
        'Question': '❓',
        'Question + Call to Action': '❓📢',
        'Question + Problem Statement + Solution': '❓🔍💡',
        'Question + Solution': '❓💡',
        'Search Call to Action': '🔍📢',
        'Statement': '💬',
        'Statement + Call to Action': '💬📢',
        'Statement + Expectation Challenge': '💪',
        'Statement Regarding Health Symptoms': '🩺',
        'Statistics Based': '📊',
        'Topic Introduction': '🌟',
        'Offer Announcement + Exclusivity': '🔒🎁',
        'Fear of Missing Out': '😱',
        'Tactics to Try Tonight': '🌙',
        'Question + Urgency': '❓⌛',
        'Question + Offer': '❓🎁',
        'How To': '🔧',
        'How To + Treatments': '🔧💊',
        'Seniors Have Been Experiencing': '👴👵',
        'List of Symptoms': '🤒',
        'Deals': '💼'
    }

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
            tone = random.choice(tones)

        # Define the prompt for the completion
        prompt = f"Create an ad headline for {topic} with the tone {tone} and the following conditions:\n1. Engagement Format: {engagement_format}\n2. Emotional Trigger: {emotional_trigger}\n3. Tone: {tone}"

        # Use OpenAI's API to create the completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        # Extract the generated headline from the response
        headline = response.choices[0].message['content'].strip()

        # Add the emoji based on the engagement format
        emoji = engagement_format_emojis.get(engagement_format, '')
        headline_with_emoji = f"{emoji} {headline}"

        # Define the prompt for the description
        description_prompt = f"Describe the idea behind the topic {topic} in 30 words or less."

        # Use OpenAI's API to create the description
        description_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": description_prompt}
            ],
            max_tokens=60
        )

        # Get the suggested description and make sure it's 30 words or less
        description = ' '.join(description_response.choices[0].message['content'].strip().split()[:30])

        # Add the data to the Google Spreadsheet
        sheet.append_row([topic, engagement_format, emotional_trigger, tone, headline_with_emoji, description])

    # Return the confirmation message
    return f"3 headlines about {topic} have been generated."


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user']  # Get the selected user
        engagement_format = request.form['engagement_format']  # Get the selected engagement format
        emotional_trigger = request.form['emotional_trigger']  # Get the selected emotional trigger
        topic = request.form['topic']  # Get the topic
        tone = request.form['tone']  # Get the selected tone

        sheet_selected = None
        if user_input.lower() == 'matt':
            sheet_selected = spreadsheet.get_worksheet(1)  # Access sheet 2
        elif user_input.lower() == 'january':
            sheet_selected = spreadsheet.sheet1  # Access sheet 1
        else:
            return "Invalid sheet name."

        if engagement_format.lower() == 'random':
            engagement_format = random.choice(engagement_formats)

        if emotional_trigger.lower() == 'random':
            emotional_trigger = random.choice(emotional_triggers)

        if tone.lower() == 'random':
            tone = random.choice(tones)

        description = generate_headlines(sheet_selected, topic, engagement_format, emotional_trigger, tone)
        return redirect(url_for('result', description=description))

    return render_template('index.html')


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