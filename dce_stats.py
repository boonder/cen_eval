#!/usr/bin/env python
# coding: utf-8

import os, sqlite3, pandas as pd
import csv
import yaml

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

print ("\nStats generator will execute with the following configuration:")
print (cfg)

source_folder = cfg['source_path']
target_folder = cfg['destination_path']
interval_selector = cfg['stats_interval']
histogram_bin = cfg['histogram_bin_size']

interval_translator = {'hour': 3600, 'day': 86400}
temporal_grain = interval_translator[interval_selector]

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE dce(timestamp, device_id, event_type, event_payload)")

filepaths = [source_folder+f for f in os.listdir(source_folder) if (f.startswith('ev_dump_') and f.endswith('.csv'))]
print("\nFiles to be loaded:")
print(filepaths)

df_all = pd.concat(map(pd.read_csv, filepaths))

#print("\nRows read:")
df_all.to_sql('dce', con, if_exists='append', index=False)


view_def = '''
CREATE VIEW filtered AS 
SELECT 
   timestamp,
   DATETIME(ROUND(timestamp), 'unixepoch') AS isodate,
   UPPER (device_id) as device_id,
   UPPER (event_type) as event_type,
   event_payload
FROM DCE 
WHERE
   UPPER(device_id) NOT GLOB '*[G-Z]*' AND
   LENGTH(timestamp) > 11 AND
   UPPER(event_type) in ('SQUIRREL','LIGHT','ROUND','GREEN');
'''
res = cur.execute(view_def)

res = cur.execute("select count(*) from filtered")
#print("Rows accepted:")
res.fetchall()


aggregate_view_def = '''
CREATE VIEW aggregate_count_view AS 
SELECT 
   event_type, 
   device_id, 
   floor(timestamp/{tg}) as interval,
   count(*) event_count 
FROM 
   filtered
GROUP BY
   floor(timestamp/{tg}),
   event_type, 
   device_id
'''.format(tg = temporal_grain)

res = cur.execute(aggregate_view_def)


count_stats_query = '''
SELECT
   device_id,
   event_type,
   MIN(event_count) min_count, 
   MAX(event_count) max_count, 
   AVG(event_count) mean_count 
FROM 
   aggregate_count_view
GROUP BY
   device_id,
   event_type   
'''

res = cur.execute(count_stats_query)
stats_result = res.fetchall()


fieldnames = ['device_id', 'event_type', 'min_count', 'max_count', 'mean_count']

with open(target_folder+"event_stats_per_device.csv","w") as f:
    writer = csv.writer(f)
    writer.writerow(fieldnames)
    writer.writerows(stats_result)

#histogram

hist_query = '''
SELECT 
   floor(timestamp/{tg})*{tg} as interval,
   count(*) event_count 
FROM 
   filtered
WHERE
   event_type = 'SQUIRREL'
GROUP BY
   floor(timestamp/{tg})*{tg},
   event_type
'''.format(tg = histogram_bin)

res = cur.execute(hist_query)
histogram_result = res.fetchall() 


fieldnames = ['epoch', 'squirrel_event_count']

with open(target_folder+"squirrel_histogram.csv","w") as f:
    writer = csv.writer(f)
    writer.writerow(fieldnames)
    writer.writerows(histogram_result)

con.close()
