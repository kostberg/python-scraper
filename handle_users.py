from utility_methods.utility_methods import *
import json
import urllib.request
import os


class InstaBot:

    def __init__(self):
        self.users = ['David', 'Veeti']

    # tools
    def high_value_accounts(self):
        user = input('Enter user (Veeti/David): ')
        user = user.capitalize()
        dir_path = input('Enter the path to desired folder to iterate over (either local or absolute): ')
        name = input('Enter the unique name of your refined list: ')
        if user not in self.users:
            raise ValueError('User does not exist')
        # iterate over files in dir and creates object
        directory = os.fsencode(dir_path)
        master_object = {}
        files_used = []
        for file in os.listdir(directory):
            files_used.append(file)
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                json_file = dir_path + "/" + filename
                json_object = self.json_to_dict(json_file)
                master_object = self.mergeDict(master_object, json_object)
        print(files_used)

        # handle numbers
        for key, value in master_object.items():
            # check if post is video
            if 'post_is_video' in value:
                pass
            else:
                for innerKey, innerValue in master_object[key].items():
                    if type(innerValue) is int:
                        pass
                    elif type(innerValue) is str:
                        master_object[key][innerKey] = int(innerValue.replace(',', ''))
                    else:
                        pass

        # refine the accounts by a lot of statements
        refined_accounts = {}
        for key, value in master_object.items():
            # check if post is video
            if 'post_is_video' in value:
                # videos always perform well
                refined_accounts.update({key: value})
            else:
                like_ratio = round((value['post_likes'] / value['followers']), 4)

                # refine the accounts by a lot of statements
                if like_ratio > 0.20:
                    refined_accounts.update({key: value})
                if value['post_likes'] > 5000 and value['followers'] < 25000:
                    refined_accounts.update({key: value})
                if value['post_likes'] > 10000 and value['followers'] < 50000:
                    refined_accounts.update({key: value})

        self.save_usernames(refined_accounts, 'refined_list/{}/{}'.format(user, name))

    def mergeDict(self, dict1, dict2):
        # Merge dictionaries and keep values of common keys in list
        dict3 = {**dict1, **dict2}
        for key, value in dict3.items():
            if key in dict1 and key in dict2:
                if value == dict1[key]:
                    pass
                else:
                    # check all possible values for type of key
                    if type(value["post_likes"]) == int and type(dict1[key]['post_likes']) == int:
                        likes = [int(value["post_likes"]), int(dict1[key]['post_likes'])]
                    elif type(value["post_likes"]) == int or type(dict1[key]['post_likes']) == int:
                        if type(value["post_likes"]) == str:
                            likes = [int(value["post_likes"].replace(',', '')), int(dict1[key]['post_likes'])]
                        elif type(value["post_likes"]) == int:
                            likes = [int(value["post_likes"]), int(dict1[key]['post_likes'].replace(',', ''))]
                    else:
                        likes = [int(value["post_likes"].replace(',', '')),
                                 int(dict1[key]['post_likes'].replace(',', ''))]

                    if type(value["followers"]) == int and type(dict1[key]["followers"]) == int:
                        followers = [int(value["followers"]), int(dict1[key]["followers"])]
                    elif type(value["followers"]) == int or type(dict1[key]["followers"]) == int:
                        if type(value["followers"]) == str:
                            likes = [int(value["followers"].replace(',', '')), int(dict1[key]["followers"])]
                        elif type(value["followers"]) == int:
                            likes = [int(value["followers"]), int(dict1[key]["followers"].replace(',', ''))]
                    else:
                        followers = [int(value["followers"].replace(',', '')),
                                     int(dict1[key]["followers"].replace(',', ''))]

                    dict3[key] = {'post_likes': max(likes), 'followers': max(followers)}

        return dict3

    def does_json_exist(self, filename):
        try:
            f = open('./JSON_lists/{}.json'.format(filename))
            f.close()
            return True
        except IOError:
            print("Success, filename doesn't exist")
            return False

    def json_to_dict(self, path):
        jsonFile = open(path)
        jsonString = jsonFile.read()
        jsonData = json.loads(jsonString)
        return jsonData

    def save_usernames(self, variable, filename):
        if self.does_json_exist(filename):
            pass
        else:
            with open('./JSON_lists/{}.json'.format(filename), 'w') as ftp:
                json.dump(list(variable.keys()), ftp)


if __name__ == '__main__':
    bot = InstaBot()
    bot.high_value_accounts()
    # ./JSON_folders/Veeti/iterate_over
