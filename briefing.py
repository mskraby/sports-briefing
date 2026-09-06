
Matt Skraby <skraby.matt@gmail.com>
10:52 AM (0 minutes ago)
to me

import requests, smtplib, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

api_key = os.getenv('CLAUDE_API_KEY')
email_pwd = os.getenv('EMAIL_PASSWORD')

if not api_key or not email_pwd:
    print('Missing secrets')
    exit(1)

print('Fetching news headlines...')

# Fetch news from NewsAPI (free tier)
news_queries = ['San Diego Padres', 'MLB baseball', 'NFL football', 'San Francisco 49ers']
news_data = {}

for query in news_queries:
    try:
        r = requests.get(f'https://newsapi.org/v2/everything',
            params={
                'q': query,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 3,
                'apiKey': 'demo'  # NewsAPI demo key (limited but free)
            },
            timeout=5)
        if r.status_code == 200:
            articles = r.json().get('articles', [])
            news_data[query] = [{'title': a.get('title'), 'description': a.get('description')} for a in articles]
    except:
        pass

print('Formatting briefing with Claude...')

# Ask Claude to format the news
r = requests.post('https://api.anthropic.com/v1/messages',
    headers={'x-api-key': api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
    json={
        'model': 'claude-opus-5',
        'max_tokens': 2000,
        'messages': [{
            'role': 'user',
            'content': f'Format this news into a sports briefing:\n\n{json.dumps(news_data, indent=2)}\n\nCreate sections for Padres, MLB, NFL, 49ers. For Padres include 2-3 analysis angles.'
        }]
    })

data = r.json()

briefing = None
for block in data.get('content', []):
    if block.get('type') == 'text':
        briefing = block.get('text')
        break

if not briefing:
    briefing = 'Could not generate briefing'

print('Sending emails...')
msg = MIMEMultipart()
msg['From'] = 'skraby.matt@gmail.com'
msg['To'] = 'skraby.matt@gmail.com, matt.skraby@audacy.com'
msg['Subject'] = 'Sports briefing'
msg.attach(MIMEText(briefing, 'plain'))

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
    s.login('skraby.matt@gmail.com', email_pwd)
    s.sendmail('skraby.matt@gmail.com', ['skraby.matt@gmail.com', 'matt.skraby@audacy.com'], msg.as_string())

print('Success')
