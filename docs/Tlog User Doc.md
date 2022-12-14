
# General Purpose and Objective

## “Task Log” Tlog is a simple to-do list manager script that converges tasks from multiple sources according to your prioritization with your in-flight work to create a new todo file each day.

TaskLog helps you reconcile the multiple demands on your time and attention into a single set of activities for a day with the objective that you only switch tasks when it increases productivity.

A primary goal of Tlog is to provide a small focused and achievable list of up to about 6 tasks each day.  Those tasks are the right tasks to work on because they reflect your highest priorities and obligations based on your goals and plans.  (You still have to decide what those priorities are, but not every day, because they do not change every day!  )

The flow and terminology of Tlog is that of a single day single person [Scrum](https://en.wikipedia.org/wiki/Scrum_(software_development)) [Sprint](https://en.wikipedia.org/wiki/Scrum_(software_development)#Sprint).

TaskLog is especially well suited to analytical work where your effort is to document and communicate resolutions to issues, or build software systems.


# Use.

Install tlog.  There is some flexibility, so that is in a separate section.

Run tlog.  


```
$ tlog
The journal location does not exist, so it will be created: /Users/paulsons/tltestjournal
Tlog Working Directory:  /Users/paulsons/testuser
Tlog Temporary Directory:  /Users/paulsons/tmp/tlog
No previous Journal Dir was found looking back 24 months.
total Backlog: 0 configured sprint_size: 5 sprint items: 0
The task blotter file is: blotter-2022-12-13.md
```


Among other things reported in the example above, tlog tells us the name of the task blotter file for today’s todo list.  It is <code>blotter-2022-12-13.md</code></strong>

It will be located in a subdirectory for the year and month below the  journal directory:


```
    tltestjournal/2022/12/blotter-2022-12-13.md
```


The journal directory is a running place for notes that you might keep as some folks would carry a paper bound book for notes and creativity to look back on over time.   More on that is explained below.

You can write your todo list for the day in the blotter file using a simple text editor.   VS Code is free and works great.   An editor that supports markdown and links will work best.

A task is just a bunch of text that tlog recognizes because it begins a new line with a few characters that tlog knows represents a status for the task.  The status characters that you use are the single letters ‘d’, ‘/’, ‘x’, or ‘a’.   The type a space, a dash, and a space.


      'd - ' todo (or do) are un-started tasks in files that contain tasks.

      '/ - ' in progress are tasks that are being worked on.

      'x - ' completed task.

      'a - ' abandoned are tasks that have been in the blotter or the backlog, but lost their relevance or  value. 

      's - 'scheduled tasks that have been moved out of the blotter prioritization because they have time scheduled for later.

When you run tlog again, it will clean tasks out of your list that you have completed or abandoned.  (i. e. you marked them with status of ‘x’ or ‘a’)  They aren’t gone.  The’re in a file of tasks resolved for the day:


```
    resolved/resolved-2022-12-13.md 
```


I added a couple tasks, 1 in progress, 1 todo, and ran tlog.   Tlog added some data into my blotter:


```
    # To Do
    / - do some tlog documentation
    storySource:testuser/tltestjournal/Endeavors/default/new task story.md
    titleHash:732b40d3c1

    d - eat dinner
    storySource:testuser/tltestjournal/Endeavors/default/new task story.md
    titleHash:3a259141f9
    # Scheduled
```


When you add more than 5 tasks to your list, tlog will move them to a separate task list and pull them in when you are ready.   The title hash is used to find the original task even if you change the status or make other edits.   


```
./tltestjournal/Endeavors/default/new task story.md
```


The <code>new task story.md</code></strong> file is the place where overflow tasks from your task blotter are stored.


# Making plans. Prioritize the work

Although you can create tasks quickly and easily in the task blotter, the main goal and purpose of tlog is to help you prioritize tasks.   Even the new tasks that you might add via the blotter during a day should be moved to an appropriately prioritized work plan if it can not be resolved quickly.   

Tlog reads a file system structure that you build under the Endeavors directory to feed tasks into your task blotter according to your priorities.

Endeavors are directories containing story files of tasks.  Tlog reads endeavors that you have prioritized in a file 

Tlog is not just a todo list   The main purpose of tlog is to help make sure the tasks you work on  

You can make lists of tasks in other files that end in the pattern ‘story.md’.  These story files should each be used to contain a collection of tasks that achieve a meaningful part of one of your endeavors.  

You can do goal planning and prioritize tasks Endeavors are your big goals 

Any subdirectory directory under the  <code>Endeavors</code></strong> directory, that is listed (in priority order) inside <strong><code>Endeavors/endeavors.md </code></strong>will be used to build a single list of prioritized tasks, and put the top tasks in your task blotter.

 

The example below with a top level journal directory named <code>tltestjournal </code></strong>makes 2 endeavors and creates a couple stories in each.

There is already a default endeavor and story for ‘on the fly task creation overflow from the task blotter.  This adds an additional one that needs to be added to the <code>Endeavors/endeavors.md</code></strong> file.


#### Create  Endeavor and story example


```
$ cd tltestjournal/
$ mkdir Endeavors/publish_tlog
$ echo publish_tlog >> Endeavors/endeavors.md
$ touch Endeavors/publish_tlog/'code story.md'
$ touch Endeavors/publish_tlog/'distribute story.md' 

$ mkdir Endeavors/conquer_world
$ echo conquer_world >> Endeavors/endeavors.md 
$ touch Endeavors/conquer_world/'python empire story.md'
$ touch Endeavors/conquer_world/'javascript empire story.md'
```


Tasks will flow to the blotter based on the order of the endeavors in `Endeavors/endeavors.md.`

For the example, so far that looks like this:


```
    publish_tlog
    conquer_world
```


Task contributions can be prioritized by story within an endeavor by listing them in a<code> <strong>priortized.md</strong></code> file within the endeavor directory.


```
$ echo 'python empire story.md' >>  Endeavors/conquer_world/prioritized.md
$ echo 'javascript empire story.md' >>  Endeavors/conquer_world/prioritized.md
$ cat  Endeavors/conquer_world/prioritized.md
python empire story.md
javascript empire story.md
```


Continuing the example, use a text editor such as VS Code to put some tasks in the stories


```
'Endeavors/publish_tlog/code story.mmd' 
d - finish status handling feature
d - update unit tests

'Endeavors/publish_tlog/code story.md' 
d - finish status handling feature
d - update unit tests

'Endeavors/publish_tlog/distribute story.md' 
d - write brief user doc
d - build pip installable module
d - push to github

'Endeavors/conquer_world/python empire story.md' 
d - master Zen of Python
d - find Holy Grail

'Endeavors/conquer_world/javascript empire story.md' 
d - make GUI tlog app
d - assert world power
```


Run tlog.


```
$ tlog
```


Examine the blotter file of tasks for the current day.


```
$ cat tltestjournal/2022/12/blotter-2022-12-14.md 
# To Do 
/ - do some tlog documentation
storySource:testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:732b40d3c1

d - eat dinner
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:3a259141f9

d - finish status handling feature
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/code story.md
titleHash:0729361727
d - write brief user doc
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/distribute story.md
titleHash:056040f784
d - master Zen of Python
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/conquer_world/python empire story.md
titleHash:68208f9087
d - make GUI tlog app
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/conquer_world/javascript empire story.md
titleHash:c9938925a1

# Scheduled 
```


The task blotter reads top to bottom according to the following rules.



1. Any in progress tasks that were in the task blotter when tlog was run will be in the new task blotter and are not subject to limitations on the number of tasks.   If they are not really in progress, change the status to ‘d’, todo.

        ```
        / - do some tlog documentation
        ```


2. Next, Tasks from `Endeavors/default/` are prioritized before tasks from any other Endeavors.  If ‘on the fly’ tasks have a lower priority, move them to another endeavor and story with a priority that you are managing.   Other stories can be created in `Endeavors/default/` and set higher priority than `new task story.md` by using an `Endeavors/default/prioritized.md` file.

        ```
        d - eat dinner
        storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/default/new task story.md
        titleHash:3a259141f9
        ```


3. The next two tasks come from the endeavor `publish_tlog` because it is the highest endeavor listed in `Endeavors/endeavors.md`.  Only 1 task is taken from each story based on a default of one for the story ‘maxTasks:’ setting described below.


# Managing focus vs multitasking: story maxTasks:


#### Setting maxTasks: example

Edit the` 'Endeavors/publish_tlog/code story.md'` so that the attribute ‘maxTasks’ appears followed by a colon and the value 3.   This causes tlog to accept up to 3 tasks from this story into the task blotter.

 


```
maxTasks:3
storyName:code story
d - finish status handling feature
```


Re run tlog, and note that a task that previously fit at the end of the the sprint selected for the task blotter no longer is included, but the task ‘`d - update unit tests'` from `publish_tlog/code story.md` is now included higher up in the prioritized task blotter.


```
# To Do 
/ - do some tlog documentation
storySource:testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:732b40d3c1

d - eat dinner
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:3a259141f9

d - finish status handling feature
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/code story.md
titleHash:0729361727
d - update unit tests
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/code story.md
titleHash:ee94d6d3e4

d - write brief user doc
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/distribute story.md
titleHash:056040f784
d - master Zen of Python
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/conquer_world/python empire story.md
titleHash:68208f9087

# Scheduled
```



# Tracking Scheduled work

Change the status from ‘d’ to ‘s’ on a task, for example 


```
s - write brief user doc
```


Re-run tlog and look in the blotter file.  

Now the scheduled task is placed in the `# Scheduled`  section at the bottom of the blotter file and no longer counts against the` maxTasks` that come from the `publish_tlog/distribute story.md` story, allowing <code>'<strong>d - build pip installable module</strong>'</code> to now appear iin the blotter.


```
# To Do 
/ - do some tlog documentation
storySource:testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:732b40d3c1

d - eat dinner
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/default/new task story.md
titleHash:3a259141f9

d - finish status handling feature
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/code story.md
titleHash:0729361727
d - update unit tests
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/code story.md
titleHash:ee94d6d3e4

d - build pip installable module
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/distribute story.md
titleHash:afc29ace0d
d - master Zen of Python
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/conquer_world/python empire story.md
titleHash:68208f9087

# Scheduled 
s - write brief user doc
storySource:/Users/paulsons/dev/tl3/tldev/testuser/tltestjournal/Endeavors/publish_tlog/distribute story.md
titleHash:056040f784
```



# Important limitations (currently) in tlog



* Status of tasks in the blotter will overwrite status of tasks in story files.
* Ordering changes in the blotter file do not cause update in ordering in the stories.
* The number of stories used from an endeavor does not have any constraint other than the maxTasks: value in the story files, which can be zero as a work around.
* Tlog does not have any integration between stories and actual e-mail and ticketing systems that might be sources of tasks.  These need to be manually reflected in task files.
* Tlog does not have any integrations with calendar / schedule systems.
* Tlog does not have a mobile app or a cloud store to manage tasks.


# Additional Features Needing Further Documentation



* Installation and environment settings
* Look back into historical months for most recent blotter file
* Rolling of the mont directory
* Saving state in git
* Archiving blotter files