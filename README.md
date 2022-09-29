# PYTHON MEETUP
The project was created to manage speeches at the conference through a telegram bot.

The bot has a web admin panel for more convenient management and work with the database.

## Setting up your development environment
To get started, you need to install dependencies and libraries:
```shell
pip install -r requirements.txt
```

Then create a `.env` file with environment variables:
```
TELEGRAM_BOT_TOKEN=<Token of your telegram bot>
DJANGO_SECRET_KEY=<Your Django project's secret key>
```

## Setting up the admin panel
To work with the admin panel, you must first configure it, to do this, do the following:


1. Database creation
```shell
python3 admin_panel/manage.py migrate
```
2. Create an account in the admin panel:
```shell
python3 admin_panel/manage.py createsuperuser
```
Next, in the console you will be asked to enter your login information.

3. Launching the web admin:
```shell
python3 admin_panel/manage.py runserver
```

After going through all the steps, the admin panel should start on your local host at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Work in the admin panel
After a successful login, you will see the possibility of creating a speaker, a speech and a conference in which the speech will be in the database.

The admin panel is intuitive, everything that you enter in the admin panel will be displayed for reference in the telegram bot.

## Telegram bot
To start the telegram bot, use the command:
```shell
python3 bot/bot.py
```

In the telegram bot, you have two branches - "Program" and "Ask a question to the speaker".

The first branch is informative - for understanding what will be in the program today, the second - for questions to the speaker, to which he then answers through the bot.

## Author
- [Alexander Zharyuk](https://github.com/AlexanderZharyuk/)
