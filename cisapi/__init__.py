#API Driver for the CIS Automotive API
# https://api.autodealerdata.com/
#This driver requires python 3.6 or higher
#This provides convenient wrappes for API calls and manages auth credentials

import os
import requests
import sys
import time
from datetime import date
import configparser


def makeConfig(configFile:str="CIS_API_CREDS.txt", apiKey:str="", apiKeyID:str="", stageName:str="default"):
    f=open(configFile, "w")
    s="["+stageName+"]\nAPI_KEY="+apiKey+"\nAPI_ID="+apiKeyID
    f.write(s)
    f.flush()
    f.close()

class CisApi:

    def __init__(self, apiKeyID:str=None, apiKey:str=None, configFileName:str="CIS_API_CREDS.txt"):
        """Wrapper for the CIS Automotive API. Convenient bindings to API endpoints are provided allong with credential
        management. For the most recent endpoint documentation see https://api.autodealerdata.com/docs
        If you are using an old version of the driver that is missing a binding for a new endpoint you can sill
        call the endpoint via the getWrapper(endPoint:str, params:dict) function. Simply pass the endpoint name as 
        a string and the parameters in as a keyword dictionary {"arg1": value1, "arg2":value2}"""
        self.apiKey=apiKey
        self.version="0.1.0"
        self.apiKeyID=apiKeyID
        self.configFileName="CIS_API_CREDS.txt"
        if(configFileName):
            self.configFileName=configFileName
        self.jwt=None
        self.jwtExpires=-1
        self.minTokenLifetime=360
        self.baseURL="https://api.autodealerdata.com"
        self.useRapidAPI=False
        self.timeout=180
        self.rapidAPIBaseURL="https://cis-automotive.p.rapidapi.com"
        self.rapidAPIHeaders={ 'x-rapidapi-host': "cis-automotive.p.rapidapi.com",
                                'x-rapidapi-key':""}
        self.userAgent="python-CIS-API-LIB/"+self.version

        if(self.apiKey is None):
            self.loadConfig(configFile=configFileName)
        
    def loadConfig(self, configFile:str=None, stageName:str="default"):
        if(configFile is None):
            configFile=self.configFileName

        
        
        if(configFile and os.path.isfile(configFile)):
            parser=configparser.ConfigParser()
            parser.read(configFile)
            if(stageName in parser):
                self.apiKey=parser[stageName]["API_KEY"]
                self.apiKeyID=parser[stageName]["API_ID"]
            return True
        
        raise Exception("Can not read config file: "+str(configFile))

        
    def getWrapper(self, endPoint:str, params:dict, includeJWT=True):
        """This function wraps the actual get requests made to the API. It adds any access tokens or 
        API keys to the request for you and automatically refreshes access tokens as needed."""
        if(self.apiKey is None):
            raise Exception("""No API credentials were provided. You must either set up a configuration file or 
            explicitly provide API credentials in the object constructor.""")
        headers={"User-Agent": self.userAgent}
        url=self.baseURL
        if(self.useRapidAPI):
            includeJWT=False
            url=self.rapidAPIBaseURL
            headers["x-rapidapi-host"]= self.rapidAPIHeaders["x-rapidapi-host"]
            headers["x-rapidapi-key"]=self.apiKey
        if(includeJWT):
            ttl=self.jwtExpires -time.time()
            #if our token is expired or about to expire refresh it before making the api call
            if(ttl<=self.minTokenLifetime):
                self.getToken()
            params["jwt"]=self.jwt
        if(url[-1]!="/" and endPoint[0]!="/"):# check to make sure a / exists between url and endPoint
            endPoint="/"+endPoint
        res=requests.get(url+endPoint, params=params, headers=headers, timeout=self.timeout)
        respCode=res.status_code
        j=res.json()
        if(respCode!=200):
            #print("Exception encountered calling endPoint: "+endPoint)
            #print("Msg from server: "+str(j))
            raise Exception("Exception encountered calling endPoint: "+endPoint+" Response from server: "+str(j))
        return j

    def getToken(self):
        if(self.useRapidAPI):
            return True
        endPoint="/getToken"
        
        params={"apiID":self.apiKeyID, "apiKey":self.apiKey}

        try:
            r=self.getWrapper(endPoint, params, includeJWT=False)
        except Exception as e:
            print("Please make sure you are providing the correct api keys and that your account is active and in good standing.")
            print("For a quick start guide see https://api.autodealerdata.com/APIQuickStart")
            print(e)
            return False
        if("token" in r):
            self.jwt=r["token"]
            self.jwtExpires=r["expires"]
            return True
        return False


    #static data
    def getRegions(self):
        return self.getWrapper("getRegions",{})
    def getBrands(self):
        return self.getWrapper("getBrands",{})
    def getModels(self, brandName:str):
        return self.getWrapper("getModels",{"brandName":brandName})
    def getInactiveModels(self, brandName:str):
        return self.getWrapper("getInactiveModels",{"brandName":brandName})

    #supply data
    def daysToSell(self, brandName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("daysToSell",{"brandName":brandName, "regionName":regionName})
    def daysSupply(self, brandName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("daysSupply",{"brandName":brandName, "regionName":regionName})

    #Pricing data
    def listPrice(self, brandName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("listPrice",{"brandName":brandName, "regionName":regionName})
    def salePrice(self, brandName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("salePrice",{"brandName":brandName, "regionName":regionName})
    def salePriceHistogram(self, brandName:str, modelName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("salePriceHistogram",{"brandName":brandName, "modelName":modelName, "regionName":regionName})
    def similarSalePrice(self, vin:str, regionName:str="REGION_STATE_CA", daysBack:int=45, sameYear:bool=False):
        return self.getWrapper("similarSalePrice",{"vin":vin, "daysBack":daysBack, "regionName":regionName, "sameYear":sameYear})

    #sales data
    def topModels(self, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("topModels",{ "regionName":regionName})
    def regionSales(self, brandName:str, month:date, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("regionSales",{"brandName":brandName, "month":month.isoformat(), "regionName":regionName})
    def regionDailySales(self, brandName:str, day:date, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("regionDailySales",{"brandName":brandName, "day":day.isoformat(), "regionName":regionName})

    #dealership data
    def getDealers(self, zipCode:int):
        return self.getWrapper("getDealers",{ "zipCode":zipCode})

    #vehicle data
    def vehicleHistory(self, vin:str):
        return self.getWrapper("vehicleHistory",{ "vin":vin})
    def vinDecode(self, vin:str, passEmpty:bool=False):
        return self.getWrapper("vinDecode",{ "vin":vin, "passEmpty":passEmpty})

