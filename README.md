# Project 8: User Interface, Authentication, and Brevet Times Calculator Application

The main application, the Brevet Time Calculator allows you to calculate the opening and closing times of Brevet checkpoints based on "KM" or "MILES" input. There are multiple rows for multiple checkpoints.

The user has the ability to register with the application in-order to gain functionality. The user may save their session's times calculated and access them later. Once logged in, the user will have selectors to form queries that will return data formatted in JSON or CSV format. 

# Technologies Used

Front-End:
  The front end view of the application utilized a number of different technologies. There is a base HTML template form that holds all of
  inputs, including km, and miles. The moment the user enters their input, the parameters are sent to the Flask server via AJAX. The                                  
  elements that we take the values from are extracted using jQuery. The data is sent back in JSON format and the looped over, displaying 
  each opening and closing time from ascending order with respect to KM (smallest to largest).
 
Back-End:
  The back end utilizes Python's Flask web application framework. When the raw KM, Mile, and Start-Times values are sent to the backend,
  the additional times are calculated according to Randonneurs USA's Octane Algorithm for calculating brevets. The times are formatted
  using the pyarrow package into .iso format and then sent back to the front end for displaying. 
  
  The user has the option to click 'save', which will prompt the Flask server to scrape the front end for all of the times and to store 
  the times into a MongoDB instance. The values can be retrieved in their desired formats when the user is logged in.
 
 User Profiles & Authetication:
  The users must be have authorization in order to access the MongoDB. The user is allowed to register and create an account. The 
  credentials are gathered using flask-wtforms. Upon successful registration ('username not taken'), the user may now log-in. The
  passwords are hashed for basic security purposes. Upon login the user is given an authorization token that expires in a set
  amount of time. The authetication token is attached to all requests.
  
  ![alt text](http://url/to/img.png)
  
    
  
