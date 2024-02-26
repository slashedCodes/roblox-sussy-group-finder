##################################################
#               grandpa finder 9000              #        
#                   by slashed                   #     
#                                                #     
# use responsibly. this might get you api banned #                              
##################################################

# funny #
print(f'[Roblox grandpa finder 9000]')
print(f'[     use responsibly.     ]')
print(f'')

# Imports #
from lib.utils import *
from lib.config import *

# Functions and stuff #
def main():
    wordlist = set(expand_list(matchlist))

    if verbose:
        print(f'[Info] The script is set to the {"groups and users" if mode == 1 else "only users"} mode.')

    with open(users_output_file, "w") as users_file:
        with open(group_output_file, "w") as groups_file:
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
                    users_file.write(f'https://www.roblox.com/users/{member}/profile/\n')
                    if verbose:
                        print(f'[Info] Found user: https://www.roblox.com/users/{member}/')
                    
                    if mode == 1:
                        member_group_ids = get_user_groups(member)
                        for member_group_id in member_group_ids:
                            group_score = get_group_score(member_group_id)
                            if verbose:
                                print(f'[Info] Found group: https://www.roblox.com/groups/{member_group_id}/x - {group_score}')
                            groups_file.write(f"https://www.roblox.com/groups/{member_group_id}/x - {group_score}\n")


if __name__ == "__main__":
    main()