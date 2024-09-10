# bd native interop bridge: telegram to slack message passing 

hey bd friends 👋 this bot helps crypto communities keep track of their telegram chats by sending unanswered messages to slack. it triggers at whatever interval you want (right now set at ~30 seconds for testing reasons, but you can edit it as you please). Basically if this bot guy is in a chat, and a partner message goes unanswered, it'll ping its slack pal to remind you & your team. 

## what does it do?

- watches your telegram groups
- tells you in slack if someone's message hasn't been answered
- lets you jump right to the telegram message from slack
- cleans up slack notifications once someone's replied in telegram

## how to set it up (for beginners)

don't worry if you're non technical  - this will walk you through it step by step!

1. **get the stuff you need**
   - download and install [python](https://www.python.org/downloads/) (choose the latest version)
   - download and install [pycharm community edition](https://www.jetbrains.com/pycharm/download/) (it's free!)

2. **grab the code**
   - at the top of this page, click the green "code" button
   - choose "download zip"
   - unzip the file somewhere on your computer

3. **set up the project in pycharm**
   - open pycharm
   - click "open" and find the folder you just unzipped
   - pycharm might ask if you want to create a virtual environment - say yes!

4. **install the required packages**
   - in pycharm, go to "view" > "tool windows" > "terminal"
   - in the terminal, type: `pip install -r requirements.txt`

5. **set up your telegram bot**
   - open telegram and search for "@botfather"
   - send him the message: `/newbot`
   - follow his instructions and keep the API token he gives you

6. **set up your slack app**
   - go to [slack's app page](https://api.slack.com/apps) and click "create new app"
   - choose "from scratch" and give it a name
   - go to "oauth & permissions" and scroll down to "scopes"
   - add these bot token scopes: `chat:write` and `chat:write.public`
   - go back up and click "install to workspace"
   - copy the "bot user oauth token" it gives you

7. **connect everything**
   - in your project folder, find the file named `.env.example`
   - rename it to just `.env`
   - open it and fill in your telegram token, slack token, and the ID of the slack channel you want to use

8. **run the bot**
   - in pycharm, find the file `main.py` in the `src` folder
   - right-click it and choose "run 'main'"

9. **invite the bot to your groups**
   - in telegram, add your new bot to any groups you want it to watch

and you're done! the bot should now be running and keeping an eye on your telegram groups. if you run into any trouble, feel free to ask binji in that twitter post (assuming thats where you found this)

## want to help out?

jk man i did this in like 3 hours, i'll need you to buy me food before i touch code again, don;t expect this to be maintained, but i think it should just work :) 

## legal stuff

this project is under the MIT license - basically, do whatever you want with it, just don't blame binji if something goes wrong!
