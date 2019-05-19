# About
This is a catalog of sports equipment. Users can view items for each sport or log in through google credentials to add edit or delete items.

# Getting Started
This project, creates a database, populates it with preliminary data and then runs the application for users to view this data or log in to add, edit or delete items.

# Prerequisites
- Python
- Vagrant
- VirtualBox

# Built With
This project consists of the following files:
- README.md - This readme file
- Vagrantfile - Configuration file for the Vagrant virtual machine
- database_setup.py - The Python program that creates the database
- allsports.py - The Python program that populates the database.
- application.py - The Python program that allows user to log in and view and edit the catalog items.

# Setup
1. Install Vagrant And VirtualBox
2. Clone this repository

# To Run
From the command line interface:
1. Launch Vagrant VM: `vagrant up` and Connect: `vagrant ssh`
2. Create a database, execute: `python database_setup.py`
3. Populate the database, execute: `python allsports.py`
4. Run the program for users, execute: `python application.py`
5. Go to localhost:8000 to use the application

# Acknowledgments
Udacity.com Full Stack Developer Nanodegree program - Items Catalog Project
