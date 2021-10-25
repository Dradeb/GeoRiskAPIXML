from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello world"


@app.route("/api/<string:addresse>", methods=['GET'])
def get(addresse = 'searchedaddress'):
    import numpy as np
    import requests

    searchedaddress = addresse

    dataforaddressapi = {
        'q': searchedaddress,
        'limit': 1,
        'autocomplete': 0
    }

    responseforaddressapi = requests.get('https://api-adresse.data.gouv.fr/search/', params=dataforaddressapi)
    addressdata = responseforaddressapi.json
    # print(responseforaddressapi.url)
    # print(responseforaddressapi.json())
    dictionary = responseforaddressapi.json()
    # print(dictionary.get('features')[0].get('geometry').get('label'))
    codeinsee1 = dictionary.get('features')[0].get('properties').get('id')
    adresse1 = dictionary.get('features')[0].get('properties').get('label')
    coordinatesarray = dictionary.get('features')[0].get('geometry').get('coordinates')

    array = np.array(coordinatesarray)
    latvalue = array[1]
    lonvalue = array[0]

    responseforrisk = requests.get(
        'https://errial.georisques.gouv.fr/api/cadastre/proximite/%s/%s/' % (lonvalue, latvalue))
    # print(responseforrisk.url)
    dictionary = responseforrisk.json()

    codeparcelle = dictionary.get('prefixe') + '-' + dictionary.get('section') + '-' + dictionary.get(
        'numero') + '@' + dictionary.get('commune')
    codeinsee2 = dictionary.get('commune')
    print(codeparcelle)

    finaldatarisk = {
        'codeINSEE': codeinsee2,
        'codeParcelle': codeparcelle,
        'nomAdresse': adresse1
    }

    finalresponse = requests.get('https://errial.georisques.gouv.fr/api/avis?', params=finaldatarisk)
    finaldictionary = finalresponse.json()

    print(finalresponse.url)
    risklevel = finaldictionary.get('niveauArgile')
    response = "None"

    # print(risklevel)
    if risklevel == 0:
        response = "Exposition au retrait-gonflement des sols argileux : Non"
    elif risklevel == 1:
        response = "Exposition au retrait-gonflement des sols argileux : Aléa faible"
    elif risklevel == 2:
        response = "Exposition au retrait-gonflement des sols argileux : Aléa moyen"
    elif risklevel == 3:
        response = "Exposition au retrait-gonflement des sols argileux : Aléa fort"

    return response


if __name__ == "__main__":
    app.run(debug=True)

