import os
import requests
from flask import Flask, render_template, request, send_file
import pandas as pd
from zipfile import ZipFile
import shutil
import re


application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def about():
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the user has entered
        try:
            global url1
            url1 = request.form['url']
            sampleTestInput = requests.get(url1)

            print(sampleTestInput.status_code)

            result = pd.read_csv("result.csv")

            # Opens the file path and write downs the content to a file
            # knownPics.Zip
            with open("sampleTestInput.zip", "wb") as data:
                data.write(sampleTestInput.content)
            print(data)

            # make  new directory
            os.mkdir("sampleTestINPUT")

            # Getting the contents inside main zip file
            with ZipFile("sampleTestInput.zip", "r") as zipObj:
                zipObj.extractall("sampleTestINPUT")

            # Access filenames inside the directory
            fileName = []
            for names in os.listdir("sampleTestINPUT"):
                fileName.append(names)

            os.remove("sampleTestInput.zip")
            shutil.rmtree("sampleTestINPUT")
            # Cleaning the filenames for test input file to extract 1st 4
            # characters
            cleanedFileName = []
            for i in range(len(fileName)):
                cleanedFileName.append(fileName[i].split(".", maxsplit=1)[0])
            cleanedFileName = list(map(int, cleanedFileName))

            # This is the dataframe containing filename
            sampledata = pd.DataFrame(columns=["custID"])
            sampledata["custID"] = cleanedFileName

            finalresult = pd.merge(sampledata, result,
                                   how='left', on=['custID'])
            finalresult.to_csv("Solution.csv", index=False)

        except Exception as e:
            errors.append(e)

    return render_template('about.html', errors=errors, results=results)


@application.route('/download-files/')
def download_file():
    try:
        global url1
        csvName = re.split('[. /]', url1)[7]
        return send_file("Solution.csv",
                         attachment_filename=csvName+".csv", as_attachment=True)
    except Exception as a:
        return ("Solution File Does Not Exist. Please pass the INPUT url first")


if application.config["DEBUG"]:
    @application.after_request
    def after_request(response):
        try:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response
        except Exception as e:
            return str(e)


@application.after_request
def add_header(response):
    try:
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    application.run(debug=True)
