# CIS-API

[![CIS Automotive API](https://api.autodealerdata.com/static/images/embedImgWide.png)](https://autodealerdata.com)

The CIS Automotive API provides real time sales and market data for the US automotive market with data on 40k dealers and over 575M vehicles.
This library provides convenient python bindings to the API and manages access credentials for you. 

For the most recent endpoint documentation see https://api.autodealerdata.com/docs

# Installation
The library can be installed with pip.
```pip install cisapi```

# Getting Started
* Our API can be accessed directly from us at https://api.autodealerdata.com or through the third party [RapidAPI](https://rapidapi.com/competitive-intelligence-solutions-llc-competitive-intelligence-solutions-llc-default/api/cis-automotive/). This library can handle either access method, but the access credentials must be retrieved differently. If you do not already have an account with us or with RapidAPI you must [create an account](https://autodealerdata.com/signup) to access our API.

* If you are accessing the API directly from us you must get your API keys from your [account page](https://autodealerdata.com/account), if you are using RapidAPI you must get your API key from them. Once logged into RapidAPI you can go to the [endpoint definitions](https://rapidapi.com/competitive-intelligence-solutions-llc-competitive-intelligence-solutions-llc-default/api/cis-automotive/endpoints) and retrieve your "x-rapidapi-key" from the example's request headers.
* We reccomend you create a local config file to store your API keys and help keep them out of source control. 
    * A helper function is provided to correctly format the config file and can be used with:
    ```python
    from cisapi import makeConfig
    makeConfig(configFile="CIS_API_CREDS.txt", apiKey="YOUR_API_KEY", apiKeyID="YOUR_API_KEY_ID_OR_EMPTY_STR_IF_USING_RAPIDAPI", stageName="default")
    ```
    The final config file will look like this.
    ```
    [default]
    API_KEY=YOUR_API_KEY
    API_ID=YOUR_API_KEY_ID_OR_EMPTY_STR_IF_USING_RAPIDAPI
    ```
    * Your API credentials may also be passed directly into the Library's constructor if you don't want to create a config file.
    ```python
    from cisapi import CisApi
    apiDriver=CisApi(apiKey="your key", apiKeyID="your key id") # load without config file
    apiDriver=CisApi(configFileName="yourConfigFile.txt") # load with a non default config file name
    apiDriver=CisApi() # load with default config file name
    ```
    
# Examples
Below are some basic example uses of the library. Additional generic examples are available at https://api.autodealerdata.com/examples **Every API request is billed against your quota. Some of these examples use premium endpoints and may incur overages depending on your [subscription plan](https://rapidapi.com/competitive-intelligence-solutions-llc-competitive-intelligence-solutions-llc-default/api/cis-automotive/pricing).** 
* Generic Response
    *  All successful API responses are json objects that contain various metadata keys and a "data" key with the response payload. The type of the "data" key depends on the endpoint, but is generally another json object or array. Example responses of each endpoint are available on [RapidAPI](https://rapidapi.com/competitive-intelligence-solutions-llc-competitive-intelligence-solutions-llc-default/api/cis-automotive/endpoints)
* Get Brands
```python 
from cisapi import CisApi
apiDriver=CisApi()
#apiDriver.useRapidAPI=True #set true if using RapidAPI as your provider
brands=apiDriver.getBrands()["data"]
for brand in brands:
    print(brand)
```
* Get Regions
```python 
from cisapi import CisApi
apiDriver=CisApi()
#apiDriver.useRapidAPI=True #set true if using RapidAPI as your provider
regions=apiDriver.getRegions()["data"]
for region in regions:
    print(region)
```

* Get Region Sales
```python 
#This example uses a premium endpoint that may incur 
#overages depending on your subscription plan.

from cisapi import CisApi
apiDriver=CisApi()
#apiDriver.useRapidAPI=True #set true if using RapidAPI as your provider
brands=apiDriver.getBrands()["data"]
regions=apiDriver.getRegions()["data"]
month="2020-01-01" 

dataDict={}
#utility function to manage request responses
def storeData(d:dict, brand:str, region:str, isoDate:str, data:str):
    if(not brand in d):
        d[brand]={}
    if(not region in d[brand]):
        d[brand][region]={}
    d[brand][region][isoDate]=data
def getData(d:dict, brand:str, region:str, isoDate:str):
    if(brand in d and region in d[brand] and isoDate in d[brand][region]):
        return d[brand][region][isoDate]
    return None
for brand in brands:
    for region in regions:
        resp=apiDriver.regionSales(brand, month, region)["data"]
        storeData(dataDict, brand, region, month, resp)
```

* Vin Decode
```python 
from cisapi import CisApi
import json

apiDriver=CisApi()
#apiDriver.useRapidAPI=True #set true if using RapidAPI as your provider
vins=["1G1JD6SH9J4126861",
"1GCGTEEN2H1258839",
"1HGCP268X8A157835",
"JTDKBRFU8H3039589",
"5N1AL0MN8EC541719",
"1J4GW58SXXC508639",
"1C4AJWAGXGL126679",
"WDDTG5CB9FJ021814",
"3VW4T7AU0HM062099",
"JM3KE4CY5E0389798"
]

for vin in vins:
    resp=apiDriver.vinDecode(vin)
    print(json.dumps(resp,indent=4, separators=(',', ': ')))
    
```

* Custom Endpoints
    *  When we add new endpoints to the API there may not immediately be bindings available in this library. It is still possible to use the new endpoints with an older version of the library with the getWrapper() function. This is the core function of the library that handles API requests and authentication. All other endpoint bindings are simple wrappers for this function. The following example shows how to do this.
```python
#arbitrary endpoint example
from cisapi import CisApi
import json

apiDriver=CisApi()
#apiDriver.useRapidAPI=True #set true if using RapidAPI as your provider
#both of these are valid choices for the same endpoint
customEndpointName="/getSomeNewEndPoint"
customEndpointName="getSomeNewEndPoint" 

customEndpointArguments={"arg1Name":"arg1Value", "arg2Name": "arg2Value"}

resp=apiDriver.getWrapper(customEndpointName, customEndpointArguments)
print(json.dumps(resp,indent=4, separators=(',', ': ')))
```


# License
This package is licensed under the MIT License.

# Copyright
Copyright 2021 Competitive Intelligence Solutions LLC