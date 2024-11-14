from langgraph_log_parser import *

database = "checkpoints.sqlite"
output = "files/sql_to_log_output.log"
csv_output = "files/csv_output.csv"

export_sqlite_to_log(database, output)

export_log_to_csv(output, csv_output)

event_log = load_event_log(csv_output)
print_full_analysis(event_log)
generate_prefix_tree(event_log, 'img/tree.png')