#!/bin/bash

gnome-terminal  --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; rosparam set use_sim_time true; exec bash" '\
                --window \
                --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; roslaunch estimation_pos hcc2021_final_map.launch; exec bash" '\
                --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; roslaunch estimation_pos localization_final.launch; exec bash" '\
                --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; roslaunch darknet_ros yolov2-tiny.launch; exec bash" '\
                --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; rosrun estimation_pos apriltag_localization ; exec bash" '\
                --tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/hcc_ws" -e 'bash -c "source devel/setup.bash ; rosrun estimation_pos drone_object.py; exec bash" '\
                --tab  --working-directory="/home/ee904/Downloads/drone_ex"\
		--tab  --working-directory="/home/ee904/MOLA/bob_lab/hcc-lab-2021/hcc-final-competition-2021/output"\

exit 0

