from pytrends.request import TrendReq
import requests
import yaml

session = requests.Session()
session.get('https://trends.google.com')
cookies_map = session.cookies.get_dict()
nid_cookie = cookies_map['NID']

pytrend = TrendReq(hl='en-US', tz=360, retries=3, requests_args={'headers': {'Cookie': f'NID={nid_cookie}'}})

with open("idiom list.txt", "r") as file:
	idioms = [line.strip() for line in file.readlines()]

def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

KEYWORD = " meaning"
KW_LEN = len(KEYWORD)

general_results = []
for chunk in chunks(idioms, 5):
	pytrend.build_payload([x + KEYWORD for x in chunk], timeframe='today 12-m', geo='US')
	time_data = pytrend.interest_over_time()
	averages = time_data.mean()
	if "isPartial" in averages:
		averages.drop("isPartial", axis='index', inplace=True)
	for query, value in averages.items():
		if value > 0:
			general_results.append({ "query": query[:-KW_LEN], "value": value }) # type: ignore
general_results = sorted(general_results, key=lambda item: item['value'])

scaled_results = {}
last_result = None
ratio = None
for chunk in chunks(general_results, 4):
	if last_result is not None:
		chunk.insert(0, last_result)
	pytrend.build_payload([d['query'] + KEYWORD for d in chunk], timeframe='today 12-m', geo='US')
	time_data = pytrend.interest_over_time()
	averages = time_data.mean()
	if "isPartial" in averages:
		averages.drop("isPartial", axis='index', inplace=True)
	for query, value in [(q[:-KW_LEN], v) for q, v in averages.items()]: # type: ignore
		if value > 0:
			if last_result is not None and last_result['query'] == query:
				ratio = last_result['value'] / value
			else:
				scaled_results[query] = value * (ratio or 1)
			last_result = { "query": query, "value": value }
scaled_results = dict(sorted(([key, round(value, 1)] for [key, value] in scaled_results.items()), key=lambda item: item[1], reverse=True))

print(yaml.dump(scaled_results, sort_keys=False))
