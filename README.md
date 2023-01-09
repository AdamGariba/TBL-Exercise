# TBL-Exercise

## Download
The project can be downloaded to your machine using git clone from your terminal:
```
git clone https://github.com/AdamGariba/TBL-Exercise.git
```
Go into the downloaded directory
```
cd TBL-Exercise
```
## Installation
A virtual environment needs to be created in order to download the dependicies for the project (i.e flask)
```
python -m venv venv
```
Activate that virtual environment after it has been created:

For Windows:
```
python venv/Scripts/activate
```
For Linux/macOs:
```
python venv/bin/activate
```
Add the dependencies to the virtual environment:
```
pip install -r requirements.txt
```
## Configure Database
Now the database for the project has to be initialized. This can be done with flask:
```
flask --app homebase init-db
```
The command above may take a few minutes to complete. It will have been completed successfully if you see this message in your terminal
```
Initialized the database.
```
## Run Project
Now the project can be run with the following command:
```
flask --app homebase run
```
If this command was successful you should see something like this in the terminal:
```
  * Serving Flask app 'homebase'
  * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
  * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```
Now go to your browser and type localhost:5000/ in the url bar

You should now be able to navigate the application with the following endpoints:
```
/
/team/{team_id}
/player/{player_id}
```

When you want to turn off the application, click on your terminal and press:
```
Ctrl+C (Windows/Linux)
or
Cmd+C (Mac)
```

If you have any questions please let me know!

You can reach me at my email that we have correspondance with.
