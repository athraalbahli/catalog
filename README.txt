# Logs Analysis Poject

This is a Flask application that implement CURD functionality on along with a third-party authentication & authorization service and also provide JSON endpoint 

## Getting Started

in order to run this poject you have to install some tools and have a linux environment 

### Prerequisites

* [python3](https://www.python.org/)
* [virtualBox](https://www.virtualbox.org/wiki/Downloads)
* [vagrant](https://www.vagrantup.com/downloads.html)


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
 	psql -d news -f newsdata.sql
 	```
6. clone the the repository
 	```
 	https://github.com/athraalbahli/logs_analysis.git
 	```

 7. cd into the project and run the python file
 	```
 	cd logs_analysis
 	python3 report.py
 	```

