"""
The path is a place that Unit tests can create and clean up subdirectories.
The test runner should set its current working directory to the directory with the project tests.
The parent_endeavor of the directory with the project test should include the following a line with
unit-test-tmp-dir in a .gitignore:


"""
import json
import os
import journaldir
import tlutil

uttd = "../unit-test-tmp-dir"   # perhaps: /Users/paulsons/dev/tl2/tlog/unit-test-tmp-dir

uttd_exists = os.path.isdir(uttd)

# type "dir" also has keys "name" and "listing" where listing is list of objects with a type of either:
#   "dir" or "file"
# type "file" also has keys "name" and "contents"
data_dir_tree = """[ 
  { "type": "dir",
    "name": "Endeavors",
    "listing": [ 
      { "type": "dir",
        "name": "aGoal",
        "listing": [
          { "type": "file",
            "name": "an unprioritized story.md",
            "contents": "d - task for after priority stories."
          },
          { "type": "file",
            "name": "prioritized.md",
            "contents": "small story.md\\nthe rest of the work story.md\\n"
          },
          { "type": "file",
            "name": "small story.md",
            "contents": "maxTasks: 3\\nd - start on the small story\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/small story.md\\ntitleHash:5e874c75f0\\nd - some more work on the small story\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/small story.md\\ntitleHash:4db4f19abf\\nd - refine the small story work\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/small story.md\\ntitleHash:961443447d\\nd - finish the small story!\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/small story.md\\ntitleHash:6ae341e0a3"
          },
          { "type": "file",
            "name": "the rest of the work story.md",
            "contents": "maxTasks: 0\\nd - won't grab this task unless maxTasks is greater than 0.\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/the rest of the work story.md\\ntitleHash:3d60c0647c\\nd - more of the rest of the work we won't see\\nstorySource:../unit-test-tmp-dir/Endeavors/aGoal/the rest of the work story.md\\ntitleHash:ef83b7f0c7"
          }
        ]
      }
    ]
  },
  { "type": "dir",
    "name": "journal",
    "listing": []
  }

]
"""

class DirTree:
    type_key = "type"
    type_val_dir = "dir"
    type_val_file = "file"
    name_key = "name"
    listing_key = "listing"
    contents_key = "contents"

    def __init__(self, path=None, json_data=None):
        self.path = path or os.path.abspath(uttd)
        self.json_data = json_data or data_dir_tree
        # print(f"__init__ data dir tree at: {self.path}")
        # todo create a scaffolding that deletes the dirs and files underneath what gets created here.
        #   there are various tests that write here, so cleanup can not be indiscriminate, it may break tests
        #   that run in parallel.
        #   Should find all the tests that read and write to file system, and make them create their own files
        #   and directories instead of relying on the json string data_dir_tree.
        os.makedirs(self.path, exist_ok=True)
        tree_struct = json.loads(self.json_data)
        # print(tree_struct)
        self.process_item(tree_struct, self.path, 1)

    def process_item(self, item, parent_dir, level):
        """
        Scans the item attribute as a tree structure composed of dictionaries and lists.
         - If the top level object is list, then a recursive call of this function is made for each item in the list.
         - If the top level item is a dict, it is expectd to have a 'type' key.
            - if the value if the 'type' key is 'file' then:
                - it is expected to have 'name' and 'contents' attributes, and the the value of 'name' will be used
                as a file name to be created and the value of 'contents' will be written to it.
            - if the value of the 'type' key is 'dir' then:
                - it is expected to have 'name' and 'listing' keys, and the the value of 'name' will be used
                as a directory name to be created under parent_dir.   A recursive call is made of this function passing
                the object associated with the 'listing' key, which should be a List.
        :level param should be incremented with each call to indicate te recursion depth troubleshooting with
        a debugger.
        """
        # print(f"process_item(item, {parent_dir}, {level}):", end='')
        if isinstance(item, dict):
            # print(f" has a dict ", end='')
            if DirTree.type_key in item:
                obj_type = item[DirTree.type_key]
                # print(f"with key:{DirTree.type_key}: {obj_type}")
                if obj_type == DirTree.type_val_dir:
                    if DirTree.name_key in item:
                        dir_name = item[DirTree.name_key]
                        full_dir = os.path.join(parent_dir, dir_name)
                        os.makedirs(full_dir, exist_ok=True)
                        # print(f"making dir: {full_dir}")
                        if DirTree.listing_key in item:
                            self.process_item(item[DirTree.listing_key], full_dir, level+1)
                    else:
                        raise tlutil.DataException(f"process_item(item): 'type': 'dir' has no 'name' key")
                elif obj_type == DirTree.type_val_file:
                    if DirTree.name_key in item:
                        file_name = item[DirTree.name_key]
                        file_path = os.path.join(parent_dir, file_name)
                        if DirTree.contents_key in item:
                            contents = item[DirTree.contents_key]
                            journaldir.write_filepath(contents, file_path)
                            # print(f"Writing file: {file_path}")
                        #else:  A directory with no contents key is allowed, but will be ignored.
                    else:
                        raise tlutil.DataException(f"process_item(item): 'type': 'file' has no 'name' key: {item}")
                else:
                    raise tlutil.DataException(f"process_item(item) has an unsupported 'type':{obj_type}")
            else:
                raise tlutil.DataException(f"process_item(item) an object with no 'type' key: {item}")
        elif isinstance(item, list):
        #     print(f"process_item(item, {parent_dir}, {level}) has a list:")
            for entry in item:
                self.process_item(entry, parent_dir, level+1)

        else:
            raise tlutil.DataException(f"process_item(item) has something that is not a dict or list.")



if __name__ == '__main__':
    DirTree()
