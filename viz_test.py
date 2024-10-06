import pandas as pd
import pm4py

# Ładowanie CSV do pandas DataFrame
file_path = 'files/csv_output_skip.csv'
df = pd.read_csv(file_path)
print(df)

# Formatowanie DataFrame dla PM4Py
df['timestamp'] = pd.to_datetime(df['timestamp'])
event_log = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')

# Discover the Directly-Follows Graph (DFG)
dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)

# Visualize the Directly-Follows Graph (DFG)
pm4py.vis.view_dfg(dfg, start_activities, end_activities)
