'''
Photo Search Application
'''

import argparse
import glob
import csv
import json
import uuid
from base64 import decodestring
import cv2
import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
import numpy as np

# csv database
familyPhotos = {}

# loop over the csv file
# create a dictionary (associative array/)
for i in csv.reader(open('FamilyPhotos.csv')):
    familyPhotos[i[0]] = i[1:]

# initialize BRISK feature detection method
brisk = cv2.BRISK_create()
matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
featureList = []

for imagePath in glob.glob("static/img/*.jpeg"):
    photo = cv2.imread(imagePath)
    grayscalePhoto = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
    (keypoints, descriptors) = brisk.detectAndCompute(grayscalePhoto, None)
    keypoints = np.float32([kp.pt for kp in keypoints])
    featureList.append((keypoints, descriptors, imagePath))

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/submitphoto", methods=['POST'])
def submitphoto():
    # grab the uploaded image and save it
    png_arr = request.form['photo']
    png_arr = png_arr.split(",")
    png_arr = png_arr[1].encode()
    fileId = str(uuid.uuid1()) + '.png'
    temp_file = open(fileId, "wb")
    temp_file.write(decodestring(png_arr))
    temp_file.close()

    queryImage = cv2.imread(fileId)
    os.remove(fileId)
    gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
    # brisk = cv2.BRISK_create()
    (queryKeypoints, queryDescriptors) = brisk.detectAndCompute(gray, None)
    queryKeypoints = np.float32([kp.pt for kp in queryKeypoints])

    # initialize results dictionary
    results = {}

    # loop over the featureList list and run the matcher
    for (keypoints, descriptors, imagePath) in featureList:
        # raw matches haven't been filtered through a distance ratio
        rawMatches = matcher.knnMatch(descriptors, queryDescriptors, 2)
        filteredMatches = []

        # loop over the raw matches
        for match in rawMatches:

            if len(match) == 2 and match[0].distance < match[1].distance * 0.7:
                filteredMatches.append((match[0].trainIdx, match[0].queryIdx))

        # check to see if there are enough matches to process
        if len(filteredMatches) > 40:
            ptsA = np.float32([queryKeypoints[i] for (i, _) in filteredMatches])
            ptsB = np.float32([keypoints[j] for (_, j) in filteredMatches])

            # compute the homography between the two sets of points
            # and compute the ratio of matched points
            (_, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, 4.0)

            # calculate score
            results[imagePath] = float(status.sum()) / status.size
        else:
            results[imagePath] = -1.0

    # sort matches by score
    if len(results) > 0:
        results = sorted([(v, k) for (k, v) in results.items() if v > 0], reverse=True)

    # no matches
    if len(results) == 0:
        return json.dumps({
            "description": "That photo returned no matches."})

    # match
    else:
        for (i, (score, imageLocation)) in enumerate(results):
            (title, date, description,
             location) = familyPhotos[imageLocation[imageLocation.rfind("/") + 1:]]
            return json.dumps({
                "title": title,
                "path": imageLocation,
                "date": date,
                "description": description,
                "location": location})


if __name__ == "__main__":
    app.run()
