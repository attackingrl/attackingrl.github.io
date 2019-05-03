import boto3
import re 
import pdb 
import json 
from collections import defaultdict

env_name_lookup = {
	"KickAndDefend-v0": "Kick and Defend",
	"SumoHumans-v0": "Sumo Humans", 
	"YouShallNotPassHumans-v0": "You Shall Not Pass", 
	"SumoAnts-v0": "Sumo Ants"
}

agent_lookup = {
	"random": "Random", 
	"zero": "Lifeless Zero Policy", 
	"zoo_1": "Zoo1", 
	"zoo_2": "Zoo2", 
	"zoo_3": "Zoo3", 
	"ppo2_1": "Adversary1",
	"ppo2_2": "Adversary2",
	"ppo2_3": "Adversary3"
}


class NestedDict(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

bucket_name = 'adversarial-policies-public'
prefix = 'videos'
s3 = boto3.resource('s3')
adv_policies_bucket = s3.Bucket(bucket_name)
pattern = re.compile(r'(\w*-v\d)_victim_(.*)_opponent_(.*).mp4')

all_info = []
video_files = []
for video_file in adv_policies_bucket.objects.all(): 
	fname = video_file.key.split('/')[1]
	match_obj = pattern.match(fname)
	if match_obj is None: 
		print("No pattern match found for {}".format(video_file))
		continue 
	video_files.append(video_file.key)
	components_tuple = match_obj.groups()
	components_dict = {'env': env_name_lookup.get(components_tuple[0]), 
					   'victim': agent_lookup.get(components_tuple[1]),
					   'opponent': agent_lookup.get(components_tuple[2].replace('_none', ''))
					   }
	all_info.append(components_dict)


nested = NestedDict()

env_level = defaultdict(dict)
for i, entry in enumerate(all_info):
	nested[entry['env']][entry['opponent']][entry['victim']] = video_files[i]



with open("file_list.json", "w") as fp: 
	json.dump(nested, fp, indent=4)
