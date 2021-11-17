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
        self.version="2021.09.01"
        self.apiKeyID=apiKeyID
        self.configFileName="CIS_API_CREDS.txt"
        if(configFileName):
            self.configFileName=configFileName
        self.jwt=None
        self.jwtExpires=-1
        self.minTokenLifetime=360
        self.baseURL="https://api.autodealerdata.com"
        self.useRapidAPI=False
        self.useVinAPI=False
        self.timeout=180
        self.rapidAPIBaseURL="cis-automotive.p.rapidapi.com"
        self.rapidAPIVinBaseURL="cis-vin-decoder.p.rapidapi.com"
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
        if(self.useRapidAPI or self.useVinAPI):
            headers["x-rapidapi-key"]=self.apiKey
            includeJWT=False
        if(self.useRapidAPI):
            url="https://"+self.rapidAPIBaseURL
            headers["x-rapidapi-host"]= self.rapidAPIBaseURL
        if(self.useVinAPI):
            url="https://"+self.rapidAPIVinBaseURL
            headers["x-rapidapi-host"]= self.rapidAPIVinBaseURL
            
        if(includeJWT):
            #if our token is expired or about to expire refresh it before making the api call
            if(self.needsRefresh()):
                self.getToken()
            params["jwt"]=self.jwt
        if(url[-1]!="/" and endPoint[0]!="/"):# check to make sure a / exists between url and endPoint
            endPoint="/"+endPoint
        if(url[-1]=="/" and endPoint[0]=="/"):# check to make sure a only one / exists between url and endPoint
            endPoint=endPoint[1:]
        res=requests.get(url+endPoint, params=params, headers=headers, timeout=self.timeout)
        respCode=res.status_code
        j=res.json()
        if(respCode!=200):
            #print("Exception encountered calling endPoint: "+endPoint)
            #print("Msg from server: "+str(j))
            msg="Exception encountered calling endPoint: "+endPoint
            if(respCode==401 or respCode==403):
                msg+="""\nPlease verify that you have correctly set the useRapidAPI or useVinAPI variables. The "useRapidAPI" variable corresponds
                to the CIS Automotive API via RapidAPI while "useVinAPI" corresponds to the CIS Vin Decoder API via RapidAPI.\n 
                If you have subscribed via our site (https://autodealerdata.com) you must retrieve your API keys from your account page and 
                include them in a config file or as arguments to this object's constructor. See https://api.autodealerdata.com/APIQuickStart \n
                You must have an active subscription on the corresponding API to make requests to it. Not all endpoints are available to all
                subscription plans. You can check the endpoint specific documentation at https://api.autodealerdata.com/docs \n"""

            msg+="\nResponse from server: "+str(j)
            print(msg)
            raise Exception()
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

    def needsRefresh(self, safetyFactor:float=1):
        """Returns True if token is below time to live limit. SafetyFactor determines additional constraint on time to live calculation. If you want to be 20% more conservative
        with default values you can pass 1.2 as a safetyfactor."""
        now=time.time()
        ttl=self.jwtExpires -now
        if(ttl<=(self.minTokenLifetime*safetyFactor)):
            return True
        return False

    def toDict(self):
        """Convert this object to a dictionary. Allows for easier multiprocessing while saving on getToken calls."""
        return self.__dict__.copy()

    def fromDict(self, d):
        """Set object properties based off of previous toDict() calls. Allows for easier multiprocessing while saving on getToken calls."""
        self.__dict__=d
        return

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
        return self.getWrapper("regionSales",{"brandName":brandName, "month":str(month), "regionName":regionName})

    def regionDailySales(self, brandName:str, day:date, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("regionDailySales",{"brandName":brandName, "day":str(day), "regionName":regionName})

    #dealership data
    def getDealers(self, zipCode:int):
        return self.getWrapper("getDealers",{ "zipCode":zipCode})

    def getDealersByRegion(self, regionName:str="REGION_STATE_CA", page:int=1):
        return self.getWrapper("getDealersByRegion",{"regionName":regionName, "page":page})

    def getDealersByID(self, dealerID:int):
        return self.getWrapper("getDealersByID",{"dealerID":dealerID})

    #vehicle data
    def vehicleHistory(self, vin:str):
        return self.getWrapper("vehicleHistory",{ "vin":vin})

    def vinDecode(self, vin:str, passEmpty:bool=False):
        return self.getWrapper("vinDecode",{ "vin":vin, "passEmpty":passEmpty})

    def listings(self, dealerID:int, page:int=1, newCars:bool=True):
        return self.getWrapper("listings",{"dealerID":dealerID, "page":page, "newCars":newCars})

    def valuation(self,
                  vin:str,
                  dealerID:int=0, zipCode:int=0, latitude:float=0, longitude:float=0, radius:float=0, regionName:str="", 
                  brandName:str="", modelName:str="", modelYear:int=0,
                  mileageLow:int=0, mileageHigh:int=0,
                  startDate:date=None, endDate:date=None, daysBack:int=45,
                  newCars:bool=False, extendedSearch:bool=False, sameYear:bool=False):
        pass
        args={}
        args["vin"]=vin.upper()

        if(dealerID!=0):
            args["dealerID"]=dealerID
        if(zipCode!=0):
            args["zipCode"]=zipCode
        if(latitude!=0):
            args["latitude"]=latitude
        if(longitude!=0):
            args["longitude"]=longitude
        if(radius!=0):
            args["radius"]=radius
        if(regionName!=""):
            args["regionName"]=regionName

        if(brandName!=""):
            args["brandName"]=brandName
        if(modelName!=""):
            args["modelName"]=modelName
        if(modelYear!=0):
            args["modelYear"]=modelYear
        
        if(mileageLow>0):
            args["mileageLow"]=mileageLow
        if(mileageHigh>0):
            args["mileageHigh"]=mileageHigh

        if(startDate!=None):
            args["startDate"]=startDate
        if(endDate!=None):
            args["endDate"]=endDate
        if(daysBack!=0):
            args["daysBack"]=daysBack

        args["newCars"]=newCars
        args["extendedSearch"]=extendedSearch
        args["sameYear"]=sameYear
        

        return self.getWrapper("valuation", args)

    def listings2(self, 
                  dealerID:int=0, zipCode:int=0, latitude:float=0, longitude:float=0, radius:float=0, regionName:str="", 
                  brandName:str="", modelName:str="", modelYear:int=0,
                  mileageLow:int=0, mileageHigh:int=0,
                  startDate:date=None, endDate:date=None, daysBack:int=45,
                  page:int=1, newCars:bool=True, extendedSearch:bool=False):
        args={}
        if(dealerID!=0):
            args["dealerID"]=dealerID
        if(zipCode!=0):
            args["zipCode"]=zipCode
        if(latitude!=0):
            args["latitude"]=latitude
        if(longitude!=0):
            args["longitude"]=longitude
        if(radius!=0):
            args["radius"]=radius
        if(regionName!=""):
            args["regionName"]=regionName

        if(brandName!=""):
            args["brandName"]=brandName
        if(modelName!=""):
            args["modelName"]=modelName
        if(modelYear!=0):
            args["modelYear"]=modelYear
        
        if(mileageLow>0):
            args["mileageLow"]=mileageLow
        if(mileageHigh>0):
            args["mileageHigh"]=mileageHigh

        if(startDate!=None):
            args["startDate"]=startDate
        if(endDate!=None):
            args["endDate"]=endDate
        if(daysBack!=0):
            args["daysBack"]=daysBack

        args["page"]=page
        args["newCars"]=newCars
        args["extendedSearch"]=extendedSearch

        return self.getWrapper("listings2", args)

    def listingsByDate(self, dealerID:int, startDate:date, endDate:date, page:int=1, newCars:bool=True):
        return self.getWrapper("listingsByDate",{"dealerID":dealerID, "startDate":startDate, "endDate":endDate, "page":page, "newCars":newCars})

    def listingsByRegion(self, regionName:str, modelName:str, page:int=1, newCars:bool=True, daysBack:int=45):
        return self.getWrapper("listingsByRegion",{"regionName":regionName, "modelName":modelName, "page":page, "newCars":newCars, "daysBack":daysBack})

    def listingsByRegionAndDate(self, regionName:str, modelName:str, startDate:date, endDate:date, page:int=1, newCars:bool=True):
        return self.getWrapper("listingsByRegionAndDate",{"regionName":regionName, "modelName":modelName, "startDate":startDate, "endDate":endDate, "page":page, "newCars":newCars })

    
    def listingsByZipCode(self, zipCode:int, page:int=1, newCars:bool=True, modelName:str=None):
        args={"zipCode":zipCode, "page":page, "newCars":newCars }
        if(modelName):
            args["modelName"]=modelName
        return self.getWrapper("listingsByZipCode", args)

    def listingsByZipCodeAndDate(self, zipCode:int, startDate:date, endDate:date, page:int=1, newCars:bool=True, modelName:str=None):
        args={"zipCode":zipCode, "startDate":startDate, "endDate":endDate, "page":page, "newCars":newCars }
        if(modelName):
            args["modelName"]=modelName
        return self.getWrapper("listingsByZipCodeAndDate", args)

    #market share
    def getRegionBrandMarketShare(self, brandName:str, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("getRegionBrandMarketShare", {"brandName":brandName,  "regionName":regionName})

    def getRegionMarketShare(self, regionName:str="REGION_STATE_CA"):
        return self.getWrapper("getRegionMarketShare", {"regionName":regionName})
    
    #application acceleration
    def vehicleSeen(self, vin:str, afterDate:date):
        return self.getWrapper("vehicleSeen",{"vin":vin, "afterDate":afterDate})
    
    

