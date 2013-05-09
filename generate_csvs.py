import requests, sys, json, csv, time, pickle
from local_settings import *

PICKLEFILE = 'capwords_cache.pickle'

def find_total(d, bioguide):
    count = 0
    total = 0
    for (item_bioguide, count) in d.items():
        if item_bioguide==bioguide:
            count += 1
        total += 1
    return (count, total)

def tally(r):
    total = 0
    j = json.loads(r)
    for i in j['results']:
        total += int(i['count'])
    return total
    

def main():    
    PARTIES = ('D', 'R', 'I', 'ALL')

    # fetch the results from the API
    results = {}    
    if '--refresh' in sys.argv:
        URL = 'http://capitolwords.org/api/1/dates.json?phrase=%s&percentages=true&granularity=month&apikey=%s'
        for t in TERMS:
            results[t] = {}
            for p in PARTIES:            
                query = URL % (t, API_KEY)
                if p!='ALL':
                    query += '&party=%s' % p
                print 'fetching term "%s" for party (%s)' % (t,p)
                r = requests.get(query)
                time.sleep(1)
                j = json.loads(r.text)
                for row in j['results']:
                    if results[t].get(row['month'], None) is None:
                        results[t][row['month']] = {}
                    results[t][row['month']]['party_%s_percent' % p] = row['percentage']
                    results[t][row['month']]['party_%s_count' % p] = row['count']
                    # results[t][row['month']]['party_%s_total' % p] = row['total']            
        pickle.dump(results, open(PICKLEFILE, 'w'))
    else:
        results = pickle.load(open(PICKLEFILE, 'r'))


    # flesh out missing dates
    dates = {}
    for t in TERMS:
        for y in range(1996, 2014):
            for m in range(1, 13):
                if results[t].get('%04d%02d' % (y,m), None) is None:
                    results[t]['%04d%02d' % (y,m)] = {}    


    # process into output files
    for t in TERMS:
        f = open(('%s.csv' % t).replace(' ', '_'), 'w')
        writer = csv.writer(f)

        output_row = ['year_and_month', 'year', 'month']
        for p in PARTIES:
            output_row.append('party_%s_percent' % p)
            output_row.append('party_%s_count' % p)
            # output_row.append('party_%s_total' % p)
        writer.writerow(output_row)

        for d in sorted(results[t].keys()):            
            month = int(d[-2:])
            year = int(d[:4])
            output_row = [d, year, month]
            for p in PARTIES:                
                output_row.append(results[t][d].get('party_%s_percent' % p, 0))
                output_row.append(results[t][d].get('party_%s_count' % p, 0))
                # output_row.append(results[t][d].get('party_%s_total' % p, 0))
            writer.writerow(output_row)

        f.close()
    
    
if __name__ == '__main__':
    main()    