Set-by-step installation guide

QuickStart: Setting up server
  This app is intend to serve multiple users with one server running. Each user must signup on first use, and login when using the created account. To set    up a server, please follow the instructions below.
  
To Insall and run:

Step 1: Clone the GitHub Repo:

    % git clone https://github.com/abdullahw1/Fitnest.git
    
Step 2: Make sure you have installed a version of python >= Python 3.8.5  and a version of pip >= pip 22.0.4 

Step 3: Go into the project main directory  
  
    % cd Fitnest
  
    % cd Fitnest Health Applic
    
Step 4(recommended): It's recommended to create a virtual environment so we can make sure we have correct packages

    % pip3 install venv
    % python3 -m venv venv
    % source venv/bin/activate
    
Step 5: Install all the packages and dependencies, which are all found in requirements.txt

    % pip3 install -r requirements.txt



Step 6: Simply run the server and enjoy!

    % python3 app/run.py
    
    On web browser, enter http://127.0.0.1:5025/
