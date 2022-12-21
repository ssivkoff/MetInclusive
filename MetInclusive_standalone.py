"""
  Is the Met becoming more Gender-inclusive?

  This script uses Wikidata Query Service (WQDS) to query Wikidata about the
  collection of the Metropolitan Museum of Art. Specifically, for each decade
  from 1870 - 2010, it looks at what percentage of items acquired during that
  decade were created by non-male artists.

  Simona Sivkoff-Livneh
  2022-12-21

"""
import requests

query = '''
  #defaultView:BarChart
  SELECT ?decade (COUNT(?gender) AS ?acquisitions) ?genderLabel WHERE {
    # Items in the collection (P195) of the Met (Q160236).
    ?item p:P195 ?node .
    ?node ps:P195 wd:Q160236 .
    ?node pq:P580 ?dateAcquired .
      
    # Extract the year from the acquisition date, cast to string,
    # and convert to decade by truncating the ones digit and
    # replacing it with a zero.
    BIND(YEAR(?dateAcquired) as ?yearAcquired) .
    BIND(CONCAT(SUBSTR(STR(?yearAcquired), 0, 4), "0") as ?decade) .

    ?item wdt:P170 ?artist .
    ?artist wdt:P21 ?gender . 
    VALUES ?gender {
      wd:Q6581097  # male
      wd:Q6581072  # female
      wd:Q48270    # non-binary
      wd:Q1097630  # intersex
    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  }
  GROUP BY ?decade ?genderLabel
'''

BASE_URL = 'https://query.wikidata.org/sparql'

# Send the query to Wikidata Query Service (WQDS) and request the output in
# JSON format.
r = requests.get(BASE_URL, params = {'format': 'json', 'query': query})
data = r.json()

male_acquisitions = {}
non_male_acquisitions = {}

for result in data['results']['bindings']:
    decade = int(result['decade']['value'])
    gender = result['genderLabel']['value']
    acquisitions = int(result['acquisitions']['value'])
    if gender == 'male':
        male_acquisitions[decade] = acquisitions
    else:
        non_male_acquisitions[decade] = non_male_acquisitions.get(decade, 0) + acquisitions

# For each decade, calculate what percent of new acquisitions were created by
# non-male artists.
for decade in sorted(male_acquisitions):
    percent_non_male = 100 * (non_male_acquisitions.get(decade, 0) /
                              male_acquisitions[decade])
    print('%ss : %.2f%%' % (decade, percent_non_male))
