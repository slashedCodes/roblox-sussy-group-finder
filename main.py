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

print("Roblox grandpa locator 9000")
print("")

# Functions and stuff #
def main():
    wordlist = set(expand_list(matchlist))
    # IT WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    with open(path.realpath(users_output_file), "w") as users_file:
        with open(path.realpath(group_output_file), "w") as groups_file:
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
                        Add verbose info       | done
                        Add member output file | done
                """

                for member in matched_members:
                    member_group_ids = get_user_groups(member)
                    users_file.write(f'https://www.roblox.com/users/{member}/profile\n')
                    for member_group_id in member_group_ids:
                        group_score = get_group_score(member_group_id)
                        if verbose:
                            print(f'[Info] Found group: https://www.roblox.com/groups/{member_group_id}/x - {group_score}\n')
                        groups_file.write(f"https://www.roblox.com/groups/{member_group_id}/x - {group_score}\n")


if __name__ == "__main__":
    main()