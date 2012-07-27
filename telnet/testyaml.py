import yaml
import config

with open('str.yaml') as f:
    print yaml.load(f)

# with open('str.yaml','w') as f:
#     yaml.dump(config.str, f, allow_unicode=True)
    
