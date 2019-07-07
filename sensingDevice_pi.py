import json
import requests
import copy
import Adafruit_DHT
import time
GPIO_PIN = 4

with open("/home/pi/Desktop/python/deviceToOM2MSensing.txt", mode="r") as readFile:
    sensingObj = json.load(readFile)

thing = sensingObj["Things"]               #thing dict
thingName = sensingObj["Things"]["name"]
location = sensingObj["Locations"][0]      #Location dict
locationLocation = location["location"]    #location in Location
FOI = copy.deepcopy(location)
del FOI["location"]
FOI["feature"]=locationLocation            #FOI dict

datastreamResourceName = []                
datastreamList = sensingObj["Datastreams"]
for x in range(len(datastreamList)):
    datastreamResourceName.append("Datastream"+str(x+1))

OM2Mdatastream = []                        #save to OM2M mode
for x in range(len(datastreamList)):
    name = datastreamList[x]["name"]
    description = datastreamList[x]["description"]
    observationType = datastreamList[x]["observationType"]
    unit = datastreamList[x]["unitOfMeasurement"]
    sensor = datastreamList[x]["Sensor"]
    observedProperty = datastreamList[x]["ObservedProperty"]
    smallDatastream = {}
    smallDatastream["name"] = name
    smallDatastream["description"] = description
    smallDatastream["observationType"] = observationType
    smallDatastream["unitOfMeasurement"] = unit
    bigDatastream = {}
    bigDatastream["Datastream"] = smallDatastream
    bigDatastream["Sensor"] = sensor
    bigDatastream["ObservedProperty"] = observedProperty
    OM2Mdatastream.append(bigDatastream)

import oneM2M.AE
import oneM2M.container
import oneM2M.contentInstance
import oneM2M.subscribe
AE = oneM2M.AE.AE(thingName,"Sensing")                       #create con and cin object instance
thingCon = oneM2M.container.container("Thing_Metadata")
locationCon = oneM2M.container.container("Locations")
DS_MetaCon = oneM2M.container.container("Datastream_Metadata")
FOICon = oneM2M.container.container("FeatureOfInterest")
thingCin = oneM2M.contentInstance.contentInstance("Thing_Metadata",json.dumps(thing))
locationCin = oneM2M.contentInstance.contentInstance("Location", json.dumps(location))
FOICin = oneM2M.contentInstance.contentInstance("FOI", json.dumps(FOI))

AEURL = "http://192.168.1.100:8686/~/mn-cse"     #create AE URL
conURL = AEURL + "/mn-name/"+thingName       #create con URL
cinURLThing = conURL+"/Thing_Metadata"           #create cin URL
cinURLLocation = conURL+"/Locations"
cinURLDS_Metadata = conURL+"/Datastream_Metadata"
cinURLFOI = conURL +"/FeatureOfInterest"
cinURLFOINew ="http://140.115.111.188:8282/~/mn-cse/mn-name/"+thingName+"/FeatureOfInterest" 
subURL = "http://140.115.111.189:8080/Sensing/service"
sub = oneM2M.subscribe.subscribe("Connector",subURL)
subLCD = oneM2M.subscribe.subscribe("Info_Monitor","http://192.168.1.103:8484/task")

AEheader = {"X-M2M-Origin": "admin:admin","Content-Type": "application/json;ty=2"}
conheader = {"X-M2M-Origin": "admin:admin","Content-Type": "application/json;ty=3"}
cinheader = {"X-M2M-Origin": "admin:admin","Content-Type": "application/json;ty=4"}
subheader = {"X-M2M-Origin": "admin:admin","Content-Type": "application/json;ty=23"}
requests.post(AEURL, headers=AEheader, data=AE.setAEBody())             #http post (AE)
requests.post(conURL, headers=conheader, data=thingCon.setConBody())    #http post (container)
requests.post(conURL, headers=conheader, data=locationCon.setConBody())
requests.post(conURL, headers=conheader, data=DS_MetaCon.setConBody())
requests.post(conURL, headers=conheader, data=FOICon.setConBody())
requests.post(cinURLThing, headers=cinheader, data=thingCin.setCinBody()) #http post (contentInstance)
requests.post(cinURLLocation, headers=cinheader, data=locationCin.setCinBody())
requests.post(cinURLFOI, headers=cinheader, data=FOICin.setCinBody())
cinSubURL = []
for x in range(len(OM2Mdatastream)):   #create Datastream_Metadata's cinc and Datastream container
    DS_MetaCin = oneM2M.contentInstance.contentInstance(datastreamResourceName[x], json.dumps(OM2Mdatastream[x]))
    requests.post(cinURLDS_Metadata, headers=cinheader,data=DS_MetaCin.setCinBody())
    DSCon = oneM2M.container.container(datastreamResourceName[x])
    requests.post(conURL, headers=conheader, data=DSCon.setConBody())
    cinSubURL.append(conURL+"/"+datastreamResourceName[x])
    requests.post(cinSubURL[x], headers=subheader, data=sub.setSubBody())
requests.post(cinSubURL[0], headers=subheader, data=subLCD.setSubBody()) #LCD monitor subscribe
#observation
cinURLObservation = []
observation = 1         #value
for x in range(len(datastreamList)):
     cinURLObservation.append(conURL + "/" + datastreamResourceName[x])
b=1
while True: 
    try:
        hh, tt = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, GPIO_PIN)
        temp = "%.2f"%tt
        hum = "%.2f"%hh
        print "temp=", temp, "C\thumadity =", hum, "%"
        t = str(temp)
        h = str(hum)
        time.sleep(1)
        observationProfile1 = "{\"resultTime\":\"null\",\"result\":\""+ t +"\",\"FOIResource\":\""+ cinURLFOINew+"/FOI" +"\"}"
        observationProfile2 = "{\"resultTime\":\"null\",\"result\":\""+ h +"\",\"FOIResource\":\""+ cinURLFOINew+"/FOI" +"\"}"
        ObservationCin1 = oneM2M.contentInstance.contentInstance("Observation%s" %b,observationProfile1)  #Observation ResourceName need to modify
        ObservationCin2 = oneM2M.contentInstance.contentInstance("Observation%s" %b,observationProfile2)
        requests.post(cinURLObservation[0], headers=cinheader, data=ObservationCin1.setCinBody())
        time.sleep(1)
        requests.post(cinURLObservation[1], headers=cinheader, data=ObservationCin2.setCinBody())
        b = b+1
        time.sleep(60)
    except (IOError,TypeError) as e:
        print "error"






