# bd native interop bridge: telegram to slack/discord message passing

hey bd friends 👋 this bot helps crypto communities keep track of their telegram chats by sending unanswered messages to slack or discord. it triggers at whatever interval you want (right now set at ~10 seconds for testing reasons, but you can edit it as you please). basically if this bot guy is in a chat, and a partner message goes unanswered, it'll ping its slack or discord pal to remind you & your team.

## what does it do?

- watches your telegram groups
- tells you in slack or discord if someone's message hasn't been answered
- lets you jump right to the telegram message from slack or discord
- cleans up slack/discord notifications once someone's replied in telegram

## how to set it up (for beginners)

don't worry if you're non technical - this will walk you through it step by step!

### get the stuff you need

- download and install [python](https://www.python.org/downloads/) (choose the latest version)
- download and install [pycharm community edition](https://www.jetbrains.com/pycharm/download/) (it's free!)

### grab the code

1. at the top of this page, click the green "code" button
2. choose "download zip"
3. unzip the file somewhere on your computer

### set up the project in pycharm

1. open pycharm
2. click "open" and find the folder you just unzipped
3. pycharm might ask if you want to create a virtual environment - say yes!

### install the required packages

1. in pycharm, go to "view" > "tool windows" > "terminal"
2. in the terminal, type: `pip3 install -r requirements.txt`
3. in the terminal, then type: `pip3 install "python-telegram-bot[job-queue]"`

### set up your telegram bot

1. open telegram and search for "@botfather"
2. send him the message: `/newbot`
3. follow his instructions and keep the API token he gives you

### configure your telegram bot's group privacy settings

1. in telegram, message @BotFather
2. send the command: `/mybots`
3. select your bot from the list
4. choose "Bot Settings"
5. select "Group Privacy"
6. choose "Turn off"

this step is super important! it lets your bot see all messages in the group, not just commands. without this, the bot won't work properly in group chats.

### set up your slack app (if using slack)

1. go to slack's app page and click "create new app"
2. choose "from scratch" and give it a name
3. go to "oauth & permissions" and scroll down to "scopes"
4. add these bot token scopes: `chat:write` and `chat:write.public`
5. go back up and click "install to workspace"
6. copy the "bot user oauth token" it gives you

### set up your discord webhook (if using discord)

1. go to your Discord server settings
2. click on "Integrations", then "Webhooks"
3. click "New Webhook" and choose a name and channel for it
4. copy the webhook URL (you'll need this later)

### connect everything

1. in your project folder, find the file named `.env.example`
2. rename it to just `.env`
3. open it and fill in your telegram token, and either your slack token and channel ID, or your discord webhook URL
4. set `OUTPUT_PLATFORM` to either "slack" or "discord"

### configure team member IDs

1. open the `main.py` file in your text editor
2. find the line `TEAM_MEMBER_IDS = []`
3. add the Telegram user IDs of your team members inside the brackets, separated by commas
   example: `TEAM_MEMBER_IDS = [123456789, 987654321]`

### customize unanswered message threshold

1. open the `main.py` file in your text editor
2. find the line `UNANSWERED_THRESHOLD = 10  # seconds`
3. change the number to your desired threshold in seconds

### run the bot

1. in PyCharm, find the file `main.py` in the project folder
2. right-click it and choose "Run 'main'"
3. you should see console output indicating that the bot has started

### invite the bot to your groups

1. in telegram, add your new bot to any groups you want it to watch

and you're done! the bot should now be running and keeping an eye on your telegram groups. if you run into any trouble, feel free to ask binji in that twitter post (assuming that's where you found this)

## troubleshooting

### SSL certificate issues
if you encounter SSL certificate errors when running the bot:
1. ensure you have the latest version of Python installed
2. try running this command in your terminal:
   ```
   /Applications/Python 3.x/Install Certificates.command
   ```
   replace '3.x' with your Python version number.

### bot not receiving messages
if the bot is not receiving messages:
1. ensure the bot has been added to the Telegram group
2. check that the bot has the necessary permissions in the group
3. for channels, make sure the bot is added as an admin

### messages not being sent to Slack/Discord
if messages are not being sent to Slack or Discord:
1. double-check your `.env` file to ensure all tokens and URLs are correct
2. for Slack, verify that the bot has been properly installed to your workspace
3. for Discord, ensure the webhook URL is valid and points to the correct channel

## want to help out?

jk man i did this in like 3 hours, i'll need you to buy me food before i touch code again, don;t expect this to be maintained, but i think it should just work :)

## legal stuff

this project is under the MIT license - basically, do whatever you want with it, just don't blame binji if something goes wrong!