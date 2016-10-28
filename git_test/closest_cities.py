"""
Question: Your task is to write code to determine which two of these cities are geographically closest
to each other​, “as the crow flies”.

Websites references:
https://developers.google.com/maps/documentation/geocoding/start
http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

To run the program:
python3 closest_cities.py

OR

python3 closest_cities.py -c "['Los Angeles', 'San Francisco', 'Boston', 'New York', 'Washington', 'Seattle', 'Austin', 'Chicago', 'San Diego', 'Denver', 'London', 'Toronto', 'Sydney', 'Melbourne', 'Paris', 'Singapore']"

"""

from argparse import ArgumentParser
import requests
import logging, logging.handlers
import sys
import json
import ast
from math import radians, cos, sin, asin, sqrt

__author__ = "Vaibhavi Jha"
__email__ = "vaibhavijha@gmail.com"
__status__ = "Development"

# globals
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_CONSOLE_HANDLER = logging.StreamHandler(stream=sys.stdout)
LOG_CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER = logging.getLogger('closest_cities')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(LOG_CONSOLE_HANDLER)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
API_KEY = "AIzaSyDG0q5LNcKR189qBWXyjW9CeaYXNOA2Vtg"

def closestpair_bruteforce(L):
    """
    Brute Force - O(n^2)

    @param L list of longitudes and latitudes
    """

    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r

    best = [haversine(L[0][0],L[0][1], L[1][0],L[1][1]), (L[0], L[1])]

    def testpair(p,q):
        d = haversine(p[0], p[1], q[0], q[1])
        if d < best[0]:
            best[0] = d
            best[1] = p,q

    for i in range(len(L)):
        for j in range(1, len(L)):
            if i+j < len(L):
                testpair(L[i],L[i+j])

    return best

def get_two_closest_cities(cities, logger = LOGGER):
    """
    Gets two closest cities in terms of distance

    @param cities List of Cities
    @param logger Logger to log the output
    """

    #Geocoding request and response (latitude/longitude lookup) for each city
    lat_long = []
    lat_long_city_dict = {}
    cities = ast.literal_eval(cities)

    for city in cities:
        #replace space and and also prepend Hired office. There can be muliple location with the same name(eg Santa Clara in US and Santa Clara in UK)
        #to narrow down the city, checking if the location has Hired office.
        name_of_the_city = city
        city = "Hired," + city.replace(" ", "+")
        request_uri = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (city, API_KEY)
        logger.debug("Sending HTTP Get Request to Google Maps %s" % request_uri)

        try:
            response = requests.get(request_uri)
            response.raise_for_status()
            json_data = json.loads(response.text)
            response.close()
            logger.debug('Validating json')
            if len(json_data["results"]) > 1:
                print("There are multiple locations returned for this place ----> %s <----- , Hence taking the first one! " % (city))
            location = json_data["results"][0]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            lat_long.append([lng, lat])
            lat_long_city_dict[str(lng)+str(lat)] = name_of_the_city
        except requests.exceptions.HTTPError as error:
            logger.error("Could not get settings from Google: [%s]" % error)
            return response.status_code, None, None
        except requests.exceptions.RequestException as error:
            logger.error("Problems occurred while making the HTTP Request: %s" % error)
            return errno.EPERM, None, None
        except ValueError as error:
            logger.error("Error while parsing JSON response: %s" % error)
            return -1, None, None
        except Exception as error:
            logger.error(error)
            return -3, None, None

    #find the 2 closest cities
    pair = closestpair_bruteforce(lat_long)

    return 0, lat_long_city_dict[str(pair[1][0][0])+str(pair[1][0][1])], lat_long_city_dict[str(pair[1][1][0])+str(pair[1][1][1])]

def main():
    # Handle command line arguments and options
    parser = ArgumentParser()
    parser.add_argument("-c", "--cities", required=False, help="List of Cities (e.g: ['Santa Clara', 'San Jose', 'San Diego'])")
    # Process command
    args = parser.parse_args()
    if not args.cities:
        args.cities = "['Los Angeles', 'San Francisco', 'Boston', 'New York', 'Washington', 'Seattle', 'Austin', 'Chicago', 'San Diego', 'Denver', 'London', 'Toronto', 'Sydney', 'Melbourne', 'Paris', 'Singapore']"

    print("Finding the 2 cities that are geographically closest to each other ........")
    print("Input: %s" % args.cities)
    result = get_two_closest_cities(args.cities)
    print("===================================================")
    print("Two geographically closest HIRED offices as crow flies are:")
    print(str(result[1]) + " & " + str(result[2]))
    print("===================================================")
    return 0

if __name__ == '__main__' :
    sys.exit(main())
