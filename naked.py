import requests
import json 
import datetime 
import time
import yaml 

from datetime import datetime
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')

nasa_api_key = "jzYd2PbbXjRagsWVKSrDlKG3GJQN3B4UKauMhAve"
nasa_api_url = "https://api.nasa.gov/neo/"

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  #str - string in python, zfil - zerofill, piemçram,  lai mçneða vçrtîba bûtu divu skaitïu gara vienmçr
print("Generated today's date: " + str(request_date))


print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)) #salîmç no vairâkâm url daïâm un izveidojâs viena
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key) 

print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text)) #text - saturs

if r.status_code == 200:

	json_data = json.loads(r.text) #ejot cauri elementiem

	ast_safe = [] #inicializç divus tukðos masîvus droðajiem un bîstamajaiem asteroîdiem
	ast_hazardous = []

	if 'element_count' in json_data: #tikai tad ja eksistçs element_count tad varçs tâlak
		ast_count = int(json_data['element_count']) #integer
		print("Asteroid count today: " + str(ast_count)) # izdrukâ cik ðobrîd asteroîdi

		if ast_count > 0: #ir jçga skriet cauri asteroîdiem ja to skaits ir lielâks par 0
			for val in json_data['near_earth_objects'][request_date]: #cikls, lai varçtu iterçt cauri katram
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val: 
					tmp_ast_name = val['name'] #lokâls mainîgais ar vçrtîbu
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					if 'kilometers' in val['estimated_diameter']: #ja diametrâ ir tad izveido minimâlo un maksimâlo
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3) #round - noapaïo ar decimâliem aiz komanta
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						else:  #tiek pieðíirtas vçrtîbas citâ gadîjumâ, pieðíir nereâlas vçrtîbas daþâdos gadîjumos, lai varçtu saprast, kas pa vainu un nav
							tmp_ast_diam_min = -2 
							tmp_ast_diam_max = -2
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1

					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']

					if len(val['close_approach_data']) > 0:  #ja garums ir lielâks par 0, tad ar viòu strâdâs
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:  #pârliecinâs vai ir vçrtîbas
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)  #nolasa datumu sekundçs kopð 1970gada, timest.
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')   #utc formâtâ
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S') #vietçjâ laika zona, bet dara to paðu

							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']: #vai eksistç ðâds ieraksts?
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							else:
								tmp_ast_speed = -1

							if 'kilometers' in val['close_approach_data'][0]['miss_distance']: #pârliecinâs vai bloks ir
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							else:
								tmp_ast_miss_dist = -1 # var bût -1, bet ðajâ kontekstâ tas jâsaprot atkal, ka kaut kas nebija kârtîbâ
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1

					print("------------------------------------------------------- >>") #noformçðana un izdrukas uz ekrâna
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:   # sadalîðana pa bîstamajiem un droðajiem asteroîdiem
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])  #masîvam pievieno

		else:
			print("No asteroids are going to hit earth today")  #kad netrâpîs neviens zemei

	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	if len(ast_hazardous) > 0:

		ast_hazardous.sort(key = lambda x: x[4], reverse=False)  #saraksts augoða laikâ pçc 4âs vçrtîbas masîvâ

		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))   #info par visiem

		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))  #darbîbas ar masîviem,piemçram 0 vçrtîba...
	else:
		print("No asteroids close passing earth today")

else: #íïûdas paziòojums, gadîjumâ, ja nav kods 200
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text)) 
