# Team MOLA : HCC Final competition #
## Step1
```
$ https://github.com/KaiYin77/Localization_by_Apriltag.git
```
## Git Tips
### SOP
```
$ git add . 
$ git commit -m "something"
$ git push [remote] [branch]
```
### How to add remote repo to local
```
$ git remote add <name> <url>
```
### How to fetch and merge the latest repo to local copy
```
$ git pull <remote>
```
### First time NEED to create a branch from master
```
$ git branch <new_branch_name>
``` 
### Switch to the branch
```
$ git checkout -b <your_branch_name>
```

Please copy the "darknet_ros" pakage you have use in Lab8 and Lab9 into your workspace.  
![](https://imgur.com/0dVP4uY.png)  

## Step2
Please finish the template shown below:
* hcc-final-competition-2021/hcc_ws/src/estimation_pos/src/apriltag_localization.cpp
* hcc-final-competition-2021/hcc_ws/src/estimation_pos/src/drone_object.py
* hcc-final-competition-2021/hcc_ws/src/estimation_pos/src/pyrobot_object.py

Note that you have to catkin_make your code each time after you change your code.
```
$ catkin_make
```
## Step3
After finish your code, you have to test the result.
Please remember you have to source your environment workspace if you open a new terminal.
```
$ source devel/setup.bash
```
### Implementation Method 1 (Run together)
Run ROS master on terminal(T1):
```
$ roscore
```
Run multiple roslaunch on terminal(T2):
```
$ source Run_All_[ drone / pyrobot ].sh
```
In last one terminal:
```
$ python eval.py [drone_ex_ans.txt] [ours] 
```
### Implementation Method 2 (Run seperatly)
Run ROS master:  
`$ roscore`

Set use_sim_time to true:  
`$ rosparam set use_sim_time true`  
Then, 

> open one terminal(T1)
> ```
> roslaunch estimation_pos hcc2021_final_map.launch
> ```
> open another terminal(T2)
> ```
> roslaunch estimation_pos localization_final.launch
> ```
> open another terminal(T3)
> ```
> roslaunch darknet_ros yolo_v3.launch
> ```
> open another terminal(T4)  
> ```
> rosrun estimation_pos apriltag_localization 
> ```
> open another terminal(T5)
> ```
> rosrun estimation_pos drone_object.py
> ```
> open another terminal(T6) and play the bag
> ```
> rosbag play "the bag you want to play" -r 0.1 --clock
> ```
