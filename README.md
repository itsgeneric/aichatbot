# Website Chatbot
AI Based Chatbot that analyzes Any Website.

## Project Overview
- Python based chatbot that allows the user to enter a website for analysis.
- Analysis includes description, technical description, title, links, word count and headings.
- The project also implements a basic frontend using HTML, CSS and JS to make the chatbot look like a conversational agent.
- A follow-up tool has been implemented using SQLite that temporarily stores URL data. If the same URL is entered twice by the user, the database recognises it and asks if the user wants to connect to a sales representative.
- Python Libraries used are Flask, Requests, BeautifulSoup, re, datetime and sqlite3
- This feature could potentially serve as a CRM dashboard.

## Project Objectives
- No data is stored in proprietary data and the program functions only on dynamic data.
- The chatbot must be able to intepret any given website.
- The system incorporates a database where the URL is logged in order to implement the Follow-Up Feature.
- The code is clean with comments explaining every line and follows best practices.

## Flowchart & Process Diagram

![Flowchart](https://github.com/user-attachments/assets/c23a68eb-b07a-4cc8-a4af-7b509d4fcd9b)

![Process Diagram](https://github.com/user-attachments/assets/b890015d-84a6-41a2-a987-704b6ebae7f2)

## Data Privacy
- None of the data entered by the user except for the URL is stored in any database.
- As soon as the user enters a new URL, the old data is erased.
- Only the URL entered is stored in a database that resets every 24 hours. This is done in order to implement a CRM system and notify the user if they want to talk to a sales representative.
- The website data and the conversations are loaded dynamically.

## CRM System Features
- Chatbot interactions are logged in the database.
- A Follow-Up feature as mentioned before is implemented.

## Project Demo

https://github.com/user-attachments/assets/7f5dc726-0786-4e22-8d3d-7916f46fac7e

## Installation Procedure
- Clone the Repository
- Install the required Python libraries as seen in requirements.txt
- Run app.py
- The program should work now with no runtime issues at a localhost port.
