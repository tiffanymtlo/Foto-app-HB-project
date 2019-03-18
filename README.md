# Foto

- [Introduction](#introduction)
- [Set Up](#set-up)
- [Core functionalities](#core-functionalities)
    - [Add New Collection](#Add-new-collection)
        - [From Homepage](#from-homepage)
        - [From Dropdown Menu](#from-dropdown-menu)
    - [Facial Recognition on Faces](#facial-recognition-on-faces)
        - [Collection Page](#collection-page)
        - [Person Page](#person-page)
            - [One person's page](#one-persons-page)
            - [Multiple people's page](#multiple-peoples-page)
        - [Photo Page](#photo-page)
    - [Create Unique Shareable Link for Sharing](#create-unique-shareable-link-for-sharing)
    - [Edit People's names](#edit-peoples-names)
- [Other functionalities](#other-functionalities)
    - [User Log In and Out](#user-log-in-and-out)
    - [Face Thumbnails Display](#face-thumbnails-display)
    - [Photo Display Options](#photo-display-options)
        - [List](#list)
        - [Grid](#grid)
- [Tech/Framework used](#technologies-frameworks-apis-and-libraries)


## Introduction

Foto is a smart online photo album, utilizing facial recognition technology to greatly improve user experience.

Imagine having to comb through a hundred photos just to find one with you in it. Foto solves this problem by identifying and indexing all human faces in a photo album, and gives users the ability to view only the photos they’re interested in. For example, in a wedding photo album, you can easily see just the photos that includes you, or just the ones with the bride and groom.

On the other hand, album’s owners are able to manage their collections of photos, edit names for the identified faces, create and share unique links that include only pictures of the intended receivers.

## Set Up

### Requirements
- PostgreSQL
- Python 3.6

### Installation
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

User can go to the upload page either from the homepage or from the dropdown menu:

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/upload_page.png "Upload Page")

#### From Homepage

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/upload_from_homepage.png "Upload from Homepage")

#### From Dropdown Menu

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/upload_from_dropdown.png "Upload from Dropdown")

### Facial Recognition on Faces
After the collection of photos are uploaded, the app would recognize the human faces in all the pictures and group them by person.

When the user hovers over a collection, the number of photos and the number of people identified would be shown.

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/all_collections.png "homepage")

#### Collection Page

When the user hovers over a photo in the collection, the people who were in that photo would be shown.

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/collection_page.png "collection page")

#### Person Page

When the user hovers over a photo in a person's page, that person's face would be highlighted in the photo to indicate where in the photo was this person.

#### One person's page

For example, in the screenshot below, under Tiffany's person page, her face was highlighted in the photo to show where was she located.

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/person_page.png "person page")

#### Multiple people's page

User can also select to show the subset of photos with multiple people in it. By clicking  ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/filter_icon.png "filter icon"), the user would be able to choose the people he/she desires.

For example, in the screenshots below, they show how to select multiple people and show the resulting page.

 ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/filtering_multiple_people.png "selecting multiple people")

  ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/multiple_people_page.png "person page")


#### Photo Page

When the user hovers over the photo in a photo page, all the human faces identified would be highlighted and those people would be shown on the list on the right.

 ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/photo_page.png "photo page")

 When hovering over an identified face, the corresponding person's face would be highlighted in the picture as well, and vice versa.

  ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/photo_page_hovering.png "photo page")

### Create Unique Shareable Link for Sharing

User can share either the entire collection or a subset of photos with their family and friends using the unguessable unique link provided.

By clicking ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/share_icon.png "get shareable link") in the page, the following page would show.

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/show_shareable_link.png "get shareable link")

User is able to share the subset of photos with their friends and family without sharing the entire collection. (There is also an option to share the entire collection. )

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/go_to_shareable_link.png "get shareable link")

### Edit People's names

User is able to edit names of the people identified in a collection.

By clicking ![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/edit_icon.png "edit names"), it would bring the user to the page for editing names.

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/edit_names_page.png "edit names")

## Other functionalities

### User Log In and Out


### Face Thumbnails Display

Each face thumbnail represents one person in the collection of pictures.
![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/face_thumbnails.png "face thumbnails")

### Photo Display Options

There are 2 different layouts for displaying photos: List & Grid. They are both shown below:

#### List

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/person_page.png "list display")

#### Grid

![alt text](https://github.com/tiffanymtlo/Foto-app-HB-project/blob/master/screenshots-for-README/grid_display.png "grid display")


## Technologies, frameworks, APIs and libraries
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
