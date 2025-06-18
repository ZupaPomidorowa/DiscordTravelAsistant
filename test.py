import os
import googlemaps

gmaps_key = os.environ.get('GMAPS_KEY')

gmaps = googlemaps.Client(key=gmaps_key)

address = 'aaaaa'
address_val = gmaps.addressvalidation(address, regionCode='PL')

verdict = address_val['result']['verdict']
city = address_val['result']['address']['postalAddress']['locality'].lower()

print(verdict.get("hasUnconfirmedComponents"))

if verdict.get("hasUnconfirmedComponents"):
    print('duck1')
else:
    print('duck2')
