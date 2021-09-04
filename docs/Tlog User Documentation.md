Status:  This is aspirational user documentation that has parts that are not yet implemented.
Development stories will be created to push toward functionality as described here

#General Purpose and Objective
##TaskLog is a to do list manager that helps you get tasks done to help you accomplish your goals.

TaskLog helps you reconcile the multiple demands on your time and attention into a single set of activities for a day 
with the objective that you only switch tasks when it increases productivity.

A primary goal of Tlog is to provide a small focused and achievable list of about 3 tasks for each day.  
Those tasks are the right tasks to work on because they reflect your highest priorities and obligations based
on your goals and plans.  (You still have to decide what those priorities are, but not every day, because 
they do not change every day!)

The flow and terminology of tlog is that of a single day single person Scrum Sprint.

[link to a finalized document summarizing features and Philosophy ] 

TaskLog is especially well suited to analytical work where your effort is to document and communicate resolutions to issues, or build software systems.

##TaskLog input: Sources of Tasks
TaskLog assumes that you do things related to multiple different parties that 
are disinterested in each others priorities, and allows you to draw from a list 
of tasks for each of those sources of work and manage them into your single 
threaded consciousness!  For example you may be working on a project that assigns 
you "tickets" to work on.  You have e-mail that demands attention, possibly 
multiple accounts.  You have career skills to develop, and a personal life including 
relationships with other demands.

### Sidebar on managing task size at the source
If it is possible to break tasks down at the source to things that can be 
completed in a day you should do so because it will improve transparency to 
that "project".  For example if you have Jira stories assigned to you, 
fight for an issue organization scheme that allows you to individually 
manage the creation and completion of sub tasks involved `in resolving an issue',
as opposed to having an issue that takes many days to complete.  It will make 
reconciliation with your list much easier.

### TaskLog
Tasklog represents all of your work that it can get information about in simple 
text files on a local device.  If you occasionally update your priorities, 
TaskLog will help you keep a sharp focus on the most important things.

## Terms and Object hierarchy
### Endeavor, Document, Section, Item, Subtext, Attribute.
An Endeavor is a thing like a project represented by a directory of stories or a Jira project, or maybe an e-mail account.  It is a set of prioritized "stories" needed to fulfill (or manage) the endeavor.

A Document is a file in an Endeavor directory with explanatory text under Section headings, and may represent a story issue in a Jira project (or some other remote planning system ) 

Section headings are markdown headings under which you keep notes and organize tasks.

Items are tasks todo, in progress, unfinished, planned, completed, or abandoned.  They are lines in Documents under Sections that start with a leader patten indicating which status the task is, such as 'd - ' for do or 'x - ' for done. 
	
	'd - '	todo (or do) are un started tasks in to _do_.
	
	'/ - '	in progress are tasks that are being worked on.
	
	'u - '	unfinished is how tasks show in past planing periods where they were in progress
			when tlog ran, and tlog shows the task in the current planning period as in progress.  If a task shows as unfinished for more than a few planning periods, it is too big, and should be broken into several tasks, or treated as a story.
	
	'p - '	planned are expected to be worked on in the current planning period.
	
	'x - '	completed task.
	
	'a - '	abandoned are tasks that have been in the backlog, but lost their relevance or 
			value.


    Subtext is any text below an Item or Section and is considered information about the section or item.  
        When Subtext appears before any Section or Item it is called Preamble text and is part of an unnamed section that begins a Document. Preamble text is useful for holding information about the Document, including Document attributes.

    For any line that matches '^word: ', 'word' is an attribute key and the rest of the line is it's value.
        Some attributes may have a special conventional significance in TaskLog.      
    
    An item attribute is an attribute under an Item. 
    
    A section attribute is an attribute under a Section header. (actually in an unnamed Item that is the first item in the section)
    
    A document attribute is an attribute in a document preamble. (actually in an unnamed Item in an unnamed Section that is the first section in the document.)

### The Work Flow.
#### Simple usage
assuming tlog is installed as described in '# Installing tlog'
run tlog to create an empty todo.md file

Edit todo.md to add some tasks with the 'd -' leader as described for 'Items' above.
A program editor such as VS Code or SublimeText is recommended, but any text editor will do.
as you work on tasks, mark them off as 'x - ' or 'a -' when you are done with them.
you can save todo.md and rerun tlog 
 - the completed and abandoned along with 'u -' task for any in progress tasks will be moved off to the 'completed-journal-yyyy-mm-dd.md' section heading with a heading of the form # Resolved yyyy-mm-dd' file for the day.
 - you will see that your tasks will be recorded in "$JOURNAL_DIR/Endeavors/default/new task story.md" in a section named '#New Tasks'  and augmented with a storySource: attribute indicating that is the file they are recorded in.
 - if you have too many tasks to focus on in todo.md, you can add a 'maxTasks: n' line to any story under Endeavors, including 'new task story.md' to confine the number of tasks it will contribute to in todo.md to 'n'.  For example:
    maxTasks: 4 
  will only allow 4 tasks to be in todo.md.  The rest wil be in the 'new task story.md'.



#### Usage with Endeavors
##### Day 1
1a. Create Endeavor subdirectories of $JOURNAL_DIR/Endeavors and list them by name in $JOURNAL_DIR/Endeavors/endeavors.md. 

1b. Create files names in $JOURNAL_DIR/Endeavors that end with the pattern story.md, and put some tasks in them as with todo.md above.
    For example:
        Endeavors/aGoal/goal work story.md
      - aGoal represents an entry in the Endeavors File matching a directory name under $JOURNAL_DIR/Endeavors.
      - goal work story.md represents a story file 

2. Run tlog, and a todo.md task file will be created in the journal directory containing the top tasks from each of your '*story.md' files created above.
 
3. Mark a few tasks in todo.md as complete or abandoned, and run tlog again.  
The completed and abandoned tasks will be removed from the source 
stories, and moved out of the task file and into the to the resolved-yyyy-mm-dd.md file for the day (in the current journal directory).

4. Add some tasks in todo.md. as in the *Simple Usage* section above and rerun tlog.   Tasks that contains x and a items will be moved to 'resolved-yyyy-mm-dd.md'. 

5. Temporary behavior:  new tasks up to maxTasks will flow into todo.txt
    Later behavior: count completed tasks and only pull a number of tasks for the day equaling globalMaxTasks (first hard coded, then configurable) minus the count of resolved tasks. 

_Should new tasks be pulled into the tasks file?  No for now 2020-04-19_
_see todo: 2020-12-20 write_xa_

 - the completed and abandoned tasks will be moved off to the 'resolved-yyyy-mm-dd.md' file for the day.

##### Day 2
1. Run tlog, and since no journal file exists, and no task file exists 
 matching the date, they will be created. New tasks will be pulled 
 according to 
    1. the story level max tasks settings
    2. _after 2020-12-31_, the endeavor/prioritized.md maxTask: settings
    3. _after 2020-12-31_, the Endeavors/endeavors.md maxTasks: setting

##### Merging / Modifying / duplicating todo tasks and Endeavors
Modify the content of tasks in the todo.md file and the task will be merged back into it's Endeavor story, as long as it is not resolved ('x -', or 'a -')
Whole tasks may be moved in an endeavor story to change priority order. If it is in todo.md, the todo.md version wil override the endeavor story version.
The title line of a task may be modified also according to the above rules 
Task content may be updated in the endeavor Story also, as long as it is not in the todo.md file also.      

Two tasks may not have the same title in the same endeavor story.

If you want to duplicate a task and modify it to create a new task in the todo.md file, you can do so if you:
 1. change the title (not counting the status leader) 
 2. delete the titleHash:
 3. leave the storySource: unmodified.
 
 The storySource: plus the titleHash: may be though of as the identity for a task.  
 The titeleHash: is computed from the title, not counting the leader. 

### Encouragement _after after 2020-04-19 Need Endeavors maxTasks for this_
If the top task has been completed, mild encouragement is written on stdout.
"One down"

If all tasks for the day have been completed, heavy encouragement is 
written on stdout.  "Killed it for today! (run tlog again to work ahead)"  
### Journal location 
A journal location represents single thread of activity for an individual person.  It has 3 logical sets of information: the future, the present, and the past.
#### The Future
 - The singular unified backlog of doable in a day tasks in priority order that the individual person intends to work on: The task Backlog
        - you create Endeavor directories as collections of '* story.md' files thas are squenced lists of tasks to complete.
#### The present
 - The currently in progress work, or work about to be started.
        - keeps only a single (representing today) journal file in the jounaldir/yyyy/mm directory
#### The past
 - The record of completed or abandoned tasks and any notes and files collected in the completion of the tasks
 - The record of unfinished tasks that had to roll to the next time period
        - keeps resolved files into a subdirectoy of jounaldir/yyyy/mm named resolved




##TaskLog draws tasks from competing sources.
TaskLog users must make decisions about how many tasks should be pulled from various Endeavors into the present day's work, as well as about the order in which those tasks will be listed.

You can set the maximum number of stories to pull into the working backlog. 
	By default all stories from all endeavors will be pulled.
You can set the number of stories to pull from each endeavor.
You can set the number of tasks to pull from each endeavor. 
	By default, all tasks from selected stories will be pulled.
You can set the number of tasks to pull into the working backlog.  
	By default, tasks will be pulled according to story settings as described above.
Stories or tasks from the journal directory have the highest priority.
After the journal directory, stories and tasks are ordered according to their sequence in the endeavors file, and then according to their priority within the endeavor.  (e. g. If the endeavor is a local backlog directory, the prioritized.md file is used.) 

###Flagged E-mail

###Task style subjects in e-mail

###Your Personal Journal directory
The personal journal directory is a backlog directory, as could be specified in the endeavors file, but it has additional significance:
	- The current day task file will be written there.
	- Its path will be deduced from the date and the JOURNAL_PATH environment setting. 

###Development projects

###Jira Projects

##Tasklog manages a Merged backlog
The backlog is stored in a file in the journal directory

#Functional Description
Without any command line arguments, tlog will look for task sources listed in JOURNAL_PATH/endeavors or ~/journal under the users home location native to the operating system distribution and write a task list to a journal directory.

Both the endeavors location and the journal location can be changed by setting environment variables as shown in the example tlog.env files. 

The current todo.md file is always searched for tasks. 

All lines matching the "do", "abandoned", "in progress", or "planned" patterns will be copied from story files to the current todo file.

# Before                    # After

+-----------------------+   +----------------------------------+
| preamble              |   | preamble                         |
| # day 1               |   | # day 1                          |
| d - do item           |   | u - unfinished (was in progress) |
| / - in progress item  |   | x - completed item               |   
| p - planned item      |   | # day 2                          |
| x - completed item    |   | / - in progress item             |
+-----------------------+   | p - planned item                 |
                            |                                  |
                            | # Backlog                        |
                            | d - do item                      |
                            +----------------------------------+

#TaskLog output: Journal of notes and activities

# Installing tlog

## set a shell environment based on tlog.env.sample:
    #tl2.env.sample
    JOURNAL_PATH="$HOME/Documents/journal"
    export JOURNAL_PATH
    
    TLOG_TMP = "$HOME/tmp/tlog"  # this is the default for logs, even if unset
    export TLOG_TMP

    PYTHONPATH=${HOME}/bin:$PYTHONPATH
    export PYTHONPATH
    
    PATH=${HOME}/bin::$PATH
    export PATH
    
    alias cdj='cd $(journaldir.py);pwd'
    alias tlog='python -m tlog' # shold run ${HOME}/bin/tlog.py

## install Python and the git module.

### Install python
As of 2021-08-30 the testing python is 3.7 or later.
Ensure that python interpreter is in the path either by updating an environment file based om tl2.env.sample above
or setting your .profile or .bash_profile or whatever profile matches your shell.

### Tweak for windows.   
At this point (2021-08-30) the shebang line in the .py scripts uses unix / linux syntax, and will need to be modified for 
Windows.


### install git.  make sure git init works
optionally set PYTHONUSERBASE per https://pip.pypa.io/en/latest/user_guide/#user-installs
- need to update these docs to include making the dir and setting the environment
- include infor on where the module actually goes.
pip install GitPython
   or
pip install -user GitPython  
un tar tl2_dist.tar into ${HOME}/bin based on PYTHONPATH from the environment is step 1.

## Install a program editor
Install vscode.
Add the extension 'Run On Save' 9update.  Different name working: possibly 'save and run'
 - https://code.visualstudio.com/docs/editor/extension-gallery
 - https://medium.com/better-programming/automatically-execute-bash-commands-on-save-in-vs-code-7a3100449f63#:~:text=If%20you%20don't%20already,Run%20On%20Save%20settings%20page.
 Go to Code->Preferences->Setting then select Extensions on the side bar in the window.
{
    "window.zoomLevel": 1,
    "emeraldwalk.runonsave": {
        "commands": [
            {
                // "match": "[Jj]ournal-[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9].md'",
                "match": "*.md",
                "cmd": "python -m tlog'"
            }
        ]
    
    }
}

                Run On Save for Visual Studio Code
                This extension allows configuring commands that get run whenever a file is saved in vscode.
                
                NOTE: Commands only get run when saving an existing file. Creating new files, and Save as... don't trigger the commands.
                
                Features
                Configure multiple commands that run when a file is saved
                Regex pattern matching for files that trigger commands running
                Sync and async support
                Configuration
                Add "emeraldwalk.runonsave" configuration to user or workspace settings.
                
                "shell" - (optional) shell path to be used with child_process.exec options that runs commands.
                "autoClearConsole" - (optional) clear VSCode output console every time commands run. Defaults to false.
                "commands" - array of commands that will be run whenever a file is saved.
                "match" - a regex for matching which files to run commands on
                NOTE Since this is a Regex, and also in a JSON string backslashes have to be double escaped such as when targetting folders. e.g. "match": "some\\\\folder\\\\.*"
                
                "cmd" - command to run. Can include parameters that will be replaced at runtime (see Placeholder Tokens section below).
                "isAsync" (optional) - defaults to false. If true, next command will be run before this one finishes.
                Sample Config
                This sample configuration will run echo statements including the saved file path. In this sample, the first command is async, so the second command will get executed immediately even if first hasn't completed. Since the second isn't async, the third command won't execute until the second is complete.
                # This is from a different extension:  Save andRun Ext from padjon
                {
                    "saveAndRunExt": {
                   
                 
                
                              "commands": [
                                  {
                                    "match": "\\.txt$",
                                    "cmd": "echo 'Executed in the terminal: I am a .txt file ${file}. '"
                                  },
                                  {
                                    "match": "\\.md$",
                                    "cmd": "$HOME/bin/tlog.sh"
                                  }
                              ]
                            }
                 
                }
 


                "emeraldwalk.runonsave": {
                    "commands": [
                        {
                            "match": ".*",
                            "isAsync": true,
                            "cmd": "echo 'I run for all files.'"
                        },
                        {
                            "match": "\\.txt$",
                            "cmd": "echo 'I am a .txt file ${file}.'"
                        },
                        {
                            "match": "\\.js$",
                            "cmd": "echo 'I am a .js file ${file}.'"
                        },
                        {
                            "match": ".*",
                            "cmd": "echo 'I am ${env.USERNAME}.'"
                        }
                    ]
                }
                Commands
                The following commands are exposed in the command palette:
                
                On Save: Enable
                On Save: Disable
                Placeholder Tokens
                Commands support placeholders similar to tasks.json.
                
                ${workspaceRoot}: DEPRECATED use ${workspaceFolder} instead
                ${workspaceFolder}: the path of the workspace folder of the saved file
                ${file}: path of saved file
                ${fileBasename}: saved file's basename
                ${fileDirname}: directory name of saved file
                ${fileExtname}: extension (including .) of saved file
                ${fileBasenameNoExt}: saved file's basename without extension
                ${relativeFile} - the current opened file relative to ${workspaceFolder}
                ${cwd}: current working directory (this is the working directory that vscode is running in not the project directory)
                Environment Variable Tokens
                ${env.Name}
                Links
                Marketplace
                Source Code
                License
                Apache

## Start making task stories.
make sure you set JOURNAL_PATH to a value that makes sense for your persnonal mamagement strategy.
You will want to make a shortcut in Explorer (Windows) or Finder (Mac)
run tlog to create the journal dir.
optionally, set up endeavors too.

# How it works
The "local record" is a single directory in the local file system with a child directory for each endevor.  The "local record" is used to manage versioning and syncronization with Endevor Sources.  The "local record" is a git repository.  Both Local and Remote endevors, are copied into the "local record" represented in Endevor Directory Form.  Any file updated as shown by 'git status' are added to a comit set (git add --all).  The commit is made, and labeled with {date}-source-changes.  Next the journal dir in the "local record" is recreated by scanning the Endevor directories in the "local record". A commit is made and labeled with {date}-work-needed.  Finally, the active journal dir is processed and written  to the "local record" journal dir and committed with a label {date}-work-completed.
update thid to show branched nstead that get merged. 

