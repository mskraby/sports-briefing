import requests, smtplib, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

api_key = os.getenv('CLAUDE_API_KEY')
email_pwd = os.getenv('EMAIL_PASSWORD')

if not api_key or not email_pwd:
    print('Missing secrets')
    exit(1)

print('Fetching sports news...')

# Call Claude with web search to get current news
r = requests.post('https://api.anthropic.com/v1/messages',
    headers={'x-api-key': api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
    json={
        'model': 'claude-opus-5',
        'max_tokens': 4000,
        'tools': [
            {
                'type': 'web_search',
                'name': 'web_search'
            }
        ],
        'messages': [{
            'role': 'user',
            'content': 'Search the web for today\'s top 3 news stories for each: San Diego Padres, MLB, NFL, and San Francisco 49ers. Use the web search tool to find current news. Compile into a briefing with plain text and section headers. For Padres, include 2-3 new analysis angles or talking points.'
        }]
    })

print(f'Status: {r.status_code}')
data = r.json()

if 'error' in data:
    print(f'API Error: {data}')
    exit(1)

briefing = None
for block in data.get('content', []):
    if block.get('type') == 'text':
        briefing = block.get('text')
        break

if not briefing:
    print('No text found in response')
    exit(1)

print('Sending emails...')
msg = MIMEMultipart()
msg['From'] = 'skraby.matt@gmail.com'
msg['To'] = 'skraby.matt@gmail.com, matt.skraby@audacy.com'
msg['Subject'] = 'Sports briefing'
msg.attach(MIMEText(briefing, 'plain'))

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
    s.login('skraby.matt@gmail.com', email_pwd)
    s.sendmail('skraby.matt@gmail.com', ['skraby.matt@gmail.com', 'matt.skraby@audacy.com'], msg.as_string())

print('Success - briefing sent')
