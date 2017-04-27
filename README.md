# photo-search

A photo search application written in Python, based on opencv and the flask web framework.

![static/img/screenshot.png](static/img/screenshot.png)

When my son was born, I started to get more interested in my family history. I started collecting family photographs in an effort to put together a visual record of our family. I quickly found out that I didn't know a lot about any of the photos, and they weren't very useful without some background information. So as I collected the background information I started entering it into a spreadsheet.

Basically I wanted:

* title
* description
* date (if available)
* location (if available)

Many of these photos were meant to be hung on a wall.  I wasn't going to display all this extra info with the framed photo, so I thought a good way to search the database of photos was with feature detection and opencv. You take a photo of the framed photo, and the application searches the database of photos and when it finds a match it displays the title and discription.

I'm using opencv with python bindings and flask to set up the web server. The application is being hosted on a raspberry pi on my home network. The performance isn't great at the moment, but it does work pretty well.