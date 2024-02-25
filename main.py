##################################################
#               grandpa finder 9000              #        
#                   by slashed                   #     
#                                                #     
# use responsibly. this might get you api banned #                              
##################################################

# Imports #
from os import path
from lib.utils import *
from lib.config import *

# Functions and stuff #
def main():
    # IT WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    wordlist = set(expand_list(matchlist));

    with open(path.realpath(output_file), "w") as file:
        for group_id in initial_groups:
            member_objects = get_all_members_in_group(group_id)

            # get stuff
            members = funny_func(member_objects, 0)
            usernames = funny_func(member_objects, 1)
            display_names = funny_func(member_objects, 2) 
            matched_members = match_usernames(usernames, display_names, members, wordlist)

            """
                TODO: Add modes,
                      Make the groups in the text file be sorted by member count.
                      Add verbose info

            """

            for member in matched_members:
                member_group_ids = get_user_groups(member)
                for member_group_id in member_group_ids:
                    file.write(f"https://www.roblox.com/groups/{member_group_id}/x\n")


if __name__ == "__main__":
    main()