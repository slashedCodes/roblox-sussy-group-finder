import pyjson5
from os import path

config = pyjson5.decode(open(path.realpath("config.json5")))
initial_groups = config["initial_groups"]
matchlist = config["matchlist"]
match_score_limit = config["match_score_limit"]
request_delay = config["request_delay"]

verbose = config["verbose"]
output_file = config["output_file"]
group_threshold = config["group_threshold"]
mode = config["mode"]
