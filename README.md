# Patching Count Generator

<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## About the Project
![Home](https://github.com/Anwita17/flask_project/blob/master/home_page_img.png)



This is a patching count generator which works as follows:  

* It has a login and register page to login old users and register new uers.
* It takes excel file as input and generates a downloadable report of the patching count of that month along with the charts for easier understanding.
* We can set reminder of any pending tasks.
* We can also view the pending tasks. Once the task is completed it gets deleted from the database.
* We can also mail the patching count details to any employee we want.

## Built With

* HTML
* CSS
* Bootstrap
* Flask
* Jinja2
* JavaScript

## Getting Started

We need to install the following modules in order to run this project locally on our machine:

### Prerequisites
 
* Installing Flask:
```sh
pip install flask
```

* Installing Flask_SQLALCHEMY:
```sh
pip install flask_sqlalchemy
```

* Installing pandas:
```sh
pip install pandas
```

* Installing Flask_mail:
```sh F
pip install flask_mail
```

* Installing pyrebase:
```sh
pip install pyrebase
```

* Installing APScheduler:
```sh
pip intsall APScheduler
```

* Installing Flask_apscheduler:
```sh
pip install flask_apscheduler
```


### Installation
1. Clone the repo:
   ```sh
   git clone https://github.com/Anwita17/flask_project.git
   ```
2. Run the cmd using the command:
   ```sh
   python app.py
   ```

## Usage

This app is used by DBA for their convenience for viewing the data instead of using the traditional excel sheets.

* Here a new user can register or an old user can login:
  ![Login](https://github.com/Anwita17/flask_project/blob/master/login_img.jpeg)
  
  
* Here the user can view the patching-count details for a particular month and download the report:
  ![ViewDetails](https://github.com/Anwita17/flask_project/blob/master/View_details_img.png)
  
  
* Here the user can upload the appropriate type of excel/csv file:
  ![Upload](https://github.com/Anwita17/flask_project/blob/master/upload_img.jpeg)
  
  
* Here the user can send email to the required person without logging into the user's personal mail:
  ![SendEmail](https://github.com/Anwita17/flask_project/blob/master/send_mail_img.jpeg)
  
  
* Here the user can set the email reminder for himself/herself for a particular event:
  ![Upload](https://github.com/Anwita17/flask_project/blob/master/add_rem_img.jpeg)
  
  
* Here the user can view the list of his/her reminders:
  ![Upload](https://github.com/Anwita17/flask_project/blob/master/view_rem_img.jpeg)

## Roadmap

See the [open issues](https://github.com/Anwita17/flask_project/issues) for a list of proposed features (and known issues).


## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Shobhit Gupta -          [linkedin](https://www.linkedin.com/in/shobhit-gupta-0b270215a/) - shobhit00gupta@gmail.com

Anwita Roy Chowdhury -   [linkedin](linkedin.com/in/anwita-roy-chowdhury-8720981a8) - anwita.roychowdhury@gmail.com

Project Link: [https://github.com/Anwita17/flask_project](https://github.com/Anwita17/flask_project)


## Acknowledgements

* [Code With Harry](https://www.youtube.com/watch?v=oA8brF3w5XQ&ab_channel=CodeWithHarry)
* [W3 schools](https://www.w3schools.com/html/)
* [BootStrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
* [Flask](https://flask.palletsprojects.com/)
* [Firebase](https://firebase.google.com/docs)
