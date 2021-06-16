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
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## About the Project
![Image of Yaktocat](https://github.com/Anwita17/flask_project/blob/master/about.jpg)



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
```sh 
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
  ![Image of Yaktocat](https://github.com/Anwita17/flask_project/blob/master/login_img.jpeg)
