# This is a small backend template for generating posts from youtube videos. This template is used in a company's web application as one of the several features
<br>
Demo of this sample template <br>

https://drive.google.com/file/d/1BhxbsPmU4Kb5dDOQoLM3JhAp9Mjr2suq/view?usp=sharing

# How to run on localhost <br>

## Follow the steps below: <br>

### 1. Create and activate virtual env in folder terminal where you are going to clone this repo
   `python -m venv venv` <br>
   `venv\Scripts\activate` <br>
### 2. Clone repo and install req
  `git clone https://github.com/CarlBrendt/AI_Blog_Generator.git` <br>
  `pip install -r AI_Blog_Generator/requirements.txt`

### 3. CD to AI_BLog_Generator folder <br>
  `cd AI_Blog_Generator`

### 4. SET UP .ENV VARIABLES
In the .env file you need to add all sensetive information like password or openai key. I use postgresql as a database, so you can install pg4admin to create and administer the db. <br>

### 5. Run docker a
`docker compose --build up` - run <br>
`docker-compose stop` - stop without deletion

### 6. Run on http://127.0.0.1:8000 or http://localhost:8000 and Enjoy
