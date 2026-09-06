import requests, smtplib, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

api_key = os.getenv('CLAUDE_API_KEY')
email_pwd = os.getenv('EMAIL_PASSWORD')

if not api_key or not email_pwd:
    print('ERROR: Missing secrets')
    exit(1)

print('Calling Claude API...')
r = requests.post('https://api.anthropic.com/v1/messages',
    headers={'x-api-key': api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
    json={'model': 'claude-opus-5', 'max_tokens': 1200, 'messages': [{'role': 'user', 'content': 'Top 3 news each: Padres, MLB, NFL, 49ers. Plain text, section headers. Padres: add 2-3 analysis angles.'}]})

print(f'Status: {r.status_code}')
data = r.json()

if 'error' in data:
    print(f'API Error: {json.dumps(data, indent=2)}')
    exit(1)

briefing = None
for block in data.get('content', []):
    if block.get('type') == 'text':
        briefing = block.get('text')
        break

if not briefing:
    print(f'ERROR: No text found. Response: {json.dumps(data, indent=2)}')
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

print('Success')
