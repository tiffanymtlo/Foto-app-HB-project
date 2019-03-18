# Foto

- [Introduction](#introduction)
- [Set Up/Installation](#set-up-installation)
- [Core functionalities](#core-functionalities)
    - [Add New Collection](#Add-new-collection)
        - [From Homepage](#from-homepage)
        - [From Dropdown Menu](#from-dropdown-menu)
    - [Facial Recognition on Faces](#facial-recognition-on-faces)
        - [Collection Page](#collection-page)
        - [Person Page](#person-page)
        - [Photo Page](#photo-page)
    - [Create Unique Shareable Link](#create-unique-shareable-link)
        - [Share Entire Collection](#share-entire-collection)
        - [Share Persons Page](#share-persons-page)
            - [One Person](#one-person)
            - [Multiple People](#multiple-people)
    - [Edit People's names](#edit-peoples-names)
- [Other functionalities](#other-functionalities)
    - [User Log In and Out](#user-log-in-and-out)
    - [Face Thumbnails Display](#face-thumbnails-display)
    - [Photo Display Options](#photo-display-options)
        - [List](#list)
        - [Grid](#grid)
- [Tech/Framework used](#technologies-frameworks-and-libraries)


## Introduction

Foto is a smart online photo album, utilizing facial recognition technology to greatly improve user experience.

Imagine having to comb through a hundred photos just to find one with you in it. Foto solves this problem by identifying and indexing all human faces in a photo album, and gives users the ability to view only the photos they’re interested in. For example, in a wedding photo album, you can easily see just the photos that includes you, or just the ones with the bride and groom.

On the other hand, album’s owners are able to manage their collections of photos, edit names for the identified faces, create and share unique links that include only pictures of the intended receivers.

## Setup/Installation

### Requirements

* PostgreSQL
* Python 3.6

Follow the instructions below to start this app on your computer:

Clone repository:
```
$ git clone https://github.com/tiffanymtlo/Foto-app-HB-project.git
```

Create a virtual environment:
```
$ virtualenv env
```

Activate the virtual environment:
```
$ source env/bin/activate
```

Install dependencies:
```
$ pip3 install -r requirements.txt
```

Create database `photos_identify`:
```
$ createdb photos_identify
```

Establish tables and relationships in the database:
```
$ python3 model.py
```

Run the app:
```
$ python3 server.py
```

## Core functionalities

### Add New Collection

#### From Homepage
#### From Dropdown Menu

### Facial Recognition on Faces
#### Collection Page
#### Person Page
#### Photo Page

### Create Unique Shareable Link
#### Share Entire Collection
#### Share Persons Page
##### One Person
##### Multiple People

### Edit People's names



## Other functionalities

### User Log In and Out
### Face Thumbnails Display
### Photo Display Options
#### List
#### Grid



## Technologies, frameworks, API and libraries
- Python
- Flask
- SQL
- SQLAlchemy
- PostgreSQL
- Jinja
- HTML/CSS
- Javascript
- jQuery
- Bootstrap (https://getbootstrap.com/)
- AWS S3 (https://aws.amazon.com/s3/)
- AWS Rekognition (https://aws.amazon.com/rekognition/)
- boto3 (https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Pillow (https://pillow.readthedocs.io/en/stable/index.html)
- Masonry (https://masonry.desandro.com/)
- UUID (https://docs.python.org/2/library/uuid.html)
