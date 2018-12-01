# Logs Analysis Poject

This is a Flask application that implement CURD functionality on along with a third-party authentication & authorization service and also provide JSON endpoint 

## Getting Started

in order to run this poject you have to install some tools and have a linux environment 

### Prerequisites

* [python3](https://www.python.org/)
* [virtualBox](https://www.virtualbox.org/wiki/Downloads)
* [vagrant](https://www.vagrantup.com/downloads.html)
* [Flask](http://flask.pocoo.org/)
* [sqlalchemy](https://www.sqlalchemy.org/)
* [oauth2client](https://oauth2client.readthedocs.io/en/latest/)
* [flask-bootstrap] (https://pythonhosted.org/Flask-Bootstrap/)


### Instructions
1. Install vaitualbox and vagrant 
2. Download a linux image inside  a newly created directory:
 	```
 	mkdir virtualdir
 	cd virtualdir
 	vagrant init ubuntu/trusty64
 	vagrant up
 	```
 
3. login to your Linux machine 
 	```
 	vagrant ssh
 	```

4. update the packages
 	```
 	sudo apt-get update && sudo apt-get upgrade
 	```

5. cd into the vagrant directory and load the data
 	```
 	cd /vagrant
 	```
6. clone the the repository
 	```
 	https://github.com/athraalbahli/catalog.git
 	```

 7. cd into the project
 	```
 	cd catalog
 	```
 8. install the required module and packages to run this application
  	```
 	pip3 install Flask
 	pip3 install flask-bootstrap
 	pip install sqlalchemy
 	pip3 install oauth2client 
 	```

9. run the application
   ```
   python3 app.py
   ```
