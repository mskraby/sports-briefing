name: Daily Sports Briefing

on:
  schedule:
    - cron: '0 15 * * *'
  workflow_dispatch:

jobs:
  send-briefing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Send briefing
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: python3 briefing.py
