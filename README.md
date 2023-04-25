# cen_eval
script to generate event data stats.

## Installation and Usage:
Modify the [conf.yaml](https://github.com/boonder/cen_eval/blob/main/config.yaml) file to set the appropriate source folder, if needed. The default input folder is expected to be a subdirectory named ```data-dump```

Verify dependencies listed in [requirements.txt](https://github.com/boonder/cen_eval/blob/main/requirements.txt). if using pip execute:
```pip install -r requirements.txt```

To run, execute:
```python3 dce_stats.py```

## Output:
The script will generate two files in the output folder specificed in [conf.yaml](https://github.com/boonder/cen_eval/blob/main/config.yaml) (default is same as the input folder ```data-dump```):

1. ```event_stats_per_device.csv```
This files containts the min, max, and mean of the counts over the interval specified in [conf.yaml](https://github.com/boonder/cen_eval/blob/main/config.yaml). hour and day are the available options. default is hour. The requirements as stated asked for a daily summary however since all of the sample data provided was for a single day, the min, max and mean values returned would have all been the same value, hence the hourly option was set as default.

2. ```squirrel_histogram.csv``` 
This files contains "histogram" data for the count of squirrel events over specified interval in [conf.yaml](https://github.com/boonder/cen_eval/blob/main/config.yaml). default is 10 seconds. Histogram may not be the best way to investigate bursts in squirrel events if the frequency and intesity of the bursts are not known beforehand as it will flatten the data in the provided bins.

## Assumptions:
1. The current implementation loads the entire batch into memory so it is assumed that a given data dump will fit in memory. A linear or partitioning approach would be recommended if larger data dumps are expected.
2. It is assumed that the provided sample is a representative sample of the data issues that will be encountered. However if this is not true the tool can be updated to handle other issues that have not been encountered so far. The tool excludes rows if any of the following issues are obseverd:
* ```device_id``` contains non hex alphabets
* ```timestamp``` has length less than 11
* ```event_type```  when converted to upper case is something other than 'SQUIRREL','LIGHT','ROUND','GREEN'


## Extensions, adding more stats etc.:
The stat generation is done in SQL using SQLite so extenstions to stats should be fairly straightforward by modifying the appropriate query. 
