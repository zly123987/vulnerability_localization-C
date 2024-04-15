import os
import shutil
from config import repo_dir, blizzard_path

def flatten_files_4_blizzard(repo):
    os.makedirs(blizzard_path, exist_ok=True)
    for root, dir, fs in os.walk(os.path.join(repo_dir, repo)):
            # if os.path.exists(os.path.join(root, 'pom.xml')):
            #     file_path = os.path.join(root, 'pom.xml')
            #     data = parse_pom(file_path)
            #     if data:
            #         gav = data.get('groupId', 'g')+'|'+data.get('artifactId', repo)+'|'+data.get('version', 'v')
            #         gav_dict[root] = gav
            #     else:
            #         gav = repo+'|'+version
            
            for f in fs:
                if not f.endswith('.java') or 'test' in root or 'Test' in root:
                    continue
                shutil.copyfile(os.path.join(root, f), os.path.join(blizzard_path, f))

                