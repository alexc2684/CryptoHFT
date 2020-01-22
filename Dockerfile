FROM python:3
ADD . /app/
RUN ls
RUN  pip install app/requirements.txt
RUN run_scraper.py
