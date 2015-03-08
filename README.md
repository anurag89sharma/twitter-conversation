# twitter-conversation
Django App for getting twitter conversation happening between 2 twitter handles

This App is deployed in heroku. 
https://twitter-conversation.herokuapp.com/

This project also consists of a file bash.sh that automates the deployment process (tested on local)
To run this file follow these steps-
  1. Get the clone of this repository to your (local)machine
  2. type "cd twitter-conversation/" and press enter
  3. type "chmod +x build.sh" and press enter
  4. Finally execute the following command -- ./build.sh

The file will firslty create a virtualenv (make sure virtualenv is installed in your machine), 
and then install all the required packages (given in requirement.txt) and then finally deploy 
then app. In the end the shell script prompts you with a url where you can go and start using 
the app.
