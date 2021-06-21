#!/usr/bin/env python2

from numpy.core.defchararray import count
from numpy.lib.financial import nper
import rospy
import numpy as np
import message_filters
import cv2
from cv_bridge import CvBridge, CvBridgeError
from darknet_ros_msgs.msg import BoundingBoxes
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry
import tf
from tf.transformations import quaternion_matrix, translation_matrix
from tf import transformations
import math
import os
import sys

pub = rospy.Publisher('/object_pose', PointStamped, queue_size=10)
pub1 = rospy.Publisher('/camera_pose', PointStamped, queue_size=10)
rospy.init_node('drone_Object', anonymous=True)
rospy.loginfo("Start D435_Object_Distance")
cv_bridge = CvBridge()

print('Try to get camera info...')

msg = rospy.wait_for_message('/camera/color/camera_info', CameraInfo, timeout=None)
#     [fx'  0  cx' Tx]
# P = [ 0  fy' cy' Ty]
#     [ 0   0   1   0]
print('Get camera info')
fx = msg.P[0]
fy = msg.P[5]
cx = msg.P[2]
cy = msg.P[6]

transform_time = 0.0
transform = Odometry()

Dist_Cam_Umb = 100
Dist_Cam_bike = 100

Umbrella = np.zeros(3)
Bicycle = np.zeros(3)
TeddyBear =  np.zeros(3)
Chair = np.zeros(3)

Umbrella_output = np.zeros(3)
Bicycle_output = np.zeros(3)
TeddyBear_output =  np.zeros(3)
Chair_output = np.zeros(3)

Umbrella_avg = []
Bicycle_avg = []
TeddyBear_avg = []
Chair_avg = []

Umbrella_tmp_avg = np.zeros(3)
Bicycle_tmp_avg = np.zeros(3)
TeddyBear_tmp_avg = np.zeros(3)
Chair_tmp_avg = np.zeros(3)

Umbrella_error = 0
Bicycle_error = 0
TeddyBear_error = 0
Chair_error = 0

person_count = 0

def main():
    depth_image_sub = message_filters.Subscriber('/camera/aligned_depth_to_color/image_raw', Image) # ('???', ???)
    bb_sub = message_filters.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes) #('???', ???)
    ts = message_filters.ApproximateTimeSynchronizer([depth_image_sub, bb_sub], 10, 0.5) #(???, ???, ???)
    ts.registerCallback(callback) #(???)
    rospy.Subscriber("apriltag_localization", Odometry, transform_cb) #("???", ???, ???)
    rospy.spin()

def transform_cb(msg):
    global transform_time
    global transform
    transform_time = msg.header.stamp.to_sec()
    transform = msg
    # print("Get transform time")
    # print(transform_time)

def callback(depth_img, bb):
    local_time = depth_img.header.stamp.to_sec()
    # print("Get local_time")
    # print(local_time)
    # you could set the time error2, 3, 4, 5 (local_time - transform_time) by yourself    
    if abs(local_time - transform_time) < 1.2 and transform_time != 0: #??? and transform_time != 0:
        # print("Time error")
        # print(local_time - transform_time)
        
        # hint: http://docs.ros.org/en/jade/api/tf/html/python/transformations.html
        # You could use "quaternion_matrix" function to find the 4x4 transform matrix
        global_transform = quaternion_matrix(np.array(
                                            [transform.pose.pose.orientation.x, 
                                             transform.pose.pose.orientation.y, 
                                             transform.pose.pose.orientation.z, 
                                             transform.pose.pose.orientation.w])) #(???)
        global_transform[0][3] = transform.pose.pose.position.x #???
        global_transform[1][3] = transform.pose.pose.position.y #???
        global_transform[2][3] = transform.pose.pose.position.z #???
        # print("transform")
        # print(global_transform)
        try:
            cv_depthimage = cv_bridge.imgmsg_to_cv2(depth_img, "32FC1")
            cv_depthimage2 = np.array(cv_depthimage, dtype=np.float32)
        except CvBridgeError as e:
            print(e)
        
        # publish camera pos in origin frame
        v1 = np.array([0,0,0,1])
        org = np.matmul(global_transform, v1)
        # print("camera_link")
        # print(object_position)
        point_message = PointStamped()
        point_message.header = depth_img.header
        point_message.header.frame_id = "origin"
        point_message.point.x = org[0]
        point_message.point.y = org[1]
        point_message.point.z = org[2]
        pub1.publish(point_message)
        
        global Umbrella
        global Umbrella_output
        global Dist_Cam_Umb
        global Dist_Cam_bike

        global Umbrella_avg
        global Bicycle_avg
        global TeddyBear_avg
        global Chair_avg

        global Umbrella_tmp_avg
        global Bicycle_tmp_avg
        global TeddyBear_tmp_avg
        global Chair_tmp_avg

        global person_count
        for i in bb.bounding_boxes:

            x_mean = (i.xmax + i.xmin) / 2
            y_mean = (i.ymax + i.ymin) / 2

            x_umb = (i.xmax*0.8 + i.xmin*1.2) / 2
            y_umb = (i.ymax*0.8 + i.ymin*1.2) / 2

            x_bike = (i.xmax + i.xmin) / 2
            y_bike = (i.ymax*3 + i.ymin) / 4

            x_chair = (i.xmax + i.xmin) / 2
            y_chair = (i.ymax*3 + i.ymin) / 4


            if i.Class == "umbrella" and i.probability >= 0.6:
                rospy.loginfo("see umbrella")
                zc = cv_depthimage2[int(y_umb)][int(x_umb)]
                v1 = np.array(getXYZ(x_umb, y_umb, zc, fx, fy, cx, cy))
                Dist_Cam_Umb = np.sqrt(v1[0]*v1[0] + v1[1]*v1[1] + v1[2]*v1[2]) / 1000
                object_position = np.matmul(global_transform, v1)
                
                if Dist_Cam_Umb > 1.6 and Dist_Cam_Umb < 1.8:
                    publish_object_location(object_position, depth_img, org, Umbrella_avg)
                
            elif i.Class == "bicycle" and i.probability >= 0.4:
                print(i)
                rospy.loginfo("see bicycle")
                zc = cv_depthimage2[int(y_bike)][int(x_bike)]
                v1 = np.array(getXYZ(x_bike, y_bike, zc, fx, fy, cx, cy))
                Dist_Cam_bike = np.sqrt(v1[0]*v1[0] + v1[1]*v1[1] + v1[2]*v1[2]) / 1000
                object_position = np.matmul(global_transform, v1)
                print('dist = ',Dist_Cam_bike)

                if(Dist_Cam_bike > 1.8 and Dist_Cam_bike < 2.5):
                    publish_object_location(object_position,depth_img, org, Bicycle_avg)
                
            elif i.Class == "teddy bear" or i.Class == "person":
                person_count = person_count + 1
                if i.Class == "teddy bear" or person_count > 10:
                    print('teddy_confidence', i.probability)
                    rospy.loginfo("see teddy bear")
                    zc = cv_depthimage2[int(y_mean)][int(x_mean)]
                    v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                    object_position = np.matmul(global_transform, v1)
                    publish_object_location(object_position,depth_img, org, TeddyBear_avg)
                                
            elif i.Class == "chair":
                rospy.loginfo("see chair")
                # calibrate 
                zc = cv_depthimage2[int(y_chair)][int(x_chair)] - 200
                v1 = np.array(getXYZ(x_chair, y_chair, zc, fx, fy, cx, cy))
                Dist_Cam_chair = np.sqrt(v1[0]*v1[0] + v1[1]*v1[1] + v1[2]*v1[2]) / 1000
                print('Dist_Chair:', Dist_Cam_chair)
                object_position = np.matmul(global_transform, v1)
                print('chair_confidence', i.probability)
                print('chair:', object_position[:3] /1000 + org[:3])
                if(Dist_Cam_chair < 3):
                    publish_object_location(object_position,depth_img, org, Chair_avg)
            ############################
            #  Student Implementation  #
            ############################
        
        List = [Umbrella_output, Bicycle, TeddyBear, Chair]

        if len(Umbrella_avg) >= 5 :
            if len(Umbrella_avg) == 5:
                for i in range(len(Umbrella_avg)):
                    Umbrella_tmp_avg[0] = Umbrella_tmp_avg[0] + Umbrella_avg[i][0]
                    Umbrella_tmp_avg[1] = Umbrella_tmp_avg[1] + Umbrella_avg[i][1]
                    Umbrella_tmp_avg[2] = Umbrella_tmp_avg[2] + Umbrella_avg[i][2]
            else:
                Umbrella_tmp_avg[0] = Umbrella_output[0] * (len(Umbrella_avg) - 1) + Umbrella_avg[len(Umbrella_avg) - 1][0]
                Umbrella_tmp_avg[1] = Umbrella_output[1] * (len(Umbrella_avg) - 1) + Umbrella_avg[len(Umbrella_avg) - 1][1]
                Umbrella_tmp_avg[2] = Umbrella_output[2] * (len(Umbrella_avg) - 1) + Umbrella_avg[len(Umbrella_avg) - 1][2]
            x_avg = Umbrella_tmp_avg[0] / len(Umbrella_avg)
            y_avg = Umbrella_tmp_avg[1] / len(Umbrella_avg)
            z_avg = Umbrella_tmp_avg[2] / len(Umbrella_avg)

            x_error = 100
            y_error = 100
            z_error = 100
            for i in range(len(Umbrella_avg)):
                tmp_x_error = np.sqrt(pow((Umbrella_avg[i][0] - x_avg), 2))
                tmp_y_error = np.sqrt(pow((Umbrella_avg[i][1] - y_avg), 2))
                tmp_z_error = np.sqrt(pow((Umbrella_avg[i][2] - z_avg), 2))
                if tmp_x_error < x_error:
                    x_error = tmp_x_error
                    Umbrella_output[0] = Umbrella_avg[i][0]
                if tmp_y_error < y_error:
                    y_error = tmp_y_error
                    Umbrella_output[1] = Umbrella_avg[i][1]
                if tmp_z_error < z_error:
                    z_error = tmp_z_error
                    Umbrella_output[2] = Umbrella_avg[i][2]
            print('Umbrella: ', Umbrella_output[0], Umbrella_output[1], Umbrella_output[2])

        if len(Bicycle_avg) >= 5:
            if len(Bicycle_avg) == 5:
                for i in range(len(Bicycle_avg)):
                    Bicycle_tmp_avg[0] = Bicycle_tmp_avg[0] + Bicycle_avg[i][0]
                    Bicycle_tmp_avg[1] = Bicycle_tmp_avg[1] + Bicycle_avg[i][1]
                    Bicycle_tmp_avg[2] = Bicycle_tmp_avg[2] + Bicycle_avg[i][2]
            else:
                Bicycle_tmp_avg[0] = Bicycle[0] * (len(Bicycle_avg) - 1) + Bicycle_avg[len(Bicycle_avg) - 1][0]
                Bicycle_tmp_avg[1] = Bicycle[1] * (len(Bicycle_avg) - 1) + Bicycle_avg[len(Bicycle_avg) - 1][1]
                Bicycle_tmp_avg[2] = Bicycle[2] * (len(Bicycle_avg) - 1) + Bicycle_avg[len(Bicycle_avg) - 1][2]
            x_avg = Bicycle_tmp_avg[0] / len(Bicycle_avg)
            y_avg = Bicycle_tmp_avg[1] / len(Bicycle_avg)
            z_avg = Bicycle_tmp_avg[2] / len(Bicycle_avg)

            x_error = 100
            y_error = 100
            z_error = 100
            for i in range(len(Bicycle_avg)):
                tmp_x_error = np.sqrt(pow((Bicycle_avg[i][0] - x_avg), 2))
                tmp_y_error = np.sqrt(pow((Bicycle_avg[i][1] - y_avg), 2))
                tmp_z_error = np.sqrt(pow((Bicycle_avg[i][2] - z_avg), 2))
                if tmp_x_error < x_error:
                    x_error = tmp_x_error
                    Bicycle[0] = Bicycle_avg[i][0]
                if tmp_y_error < y_error:
                    y_error = tmp_y_error
                    Bicycle[1] = Bicycle_avg[i][1]
                if tmp_z_error < z_error:
                    z_error = tmp_z_error
                    Bicycle[2] = Bicycle_avg[i][2]
            print('Bicycle: ', Bicycle[0], Bicycle[1], Bicycle[2])

        if len(TeddyBear_avg) > 5:
            if len(TeddyBear_avg) == 5:
                for i in range(len(TeddyBear_avg)):
                    TeddyBear_tmp_avg[0] = TeddyBear_tmp_avg[0] + TeddyBear_avg[i][0]
                    TeddyBear_tmp_avg[1] = TeddyBear_tmp_avg[1] + TeddyBear_avg[i][1]
                    TeddyBear_tmp_avg[2] = TeddyBear_tmp_avg[2] + TeddyBear_avg[i][2]
            else:
                TeddyBear_tmp_avg[0] = TeddyBear[0] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][0]
                TeddyBear_tmp_avg[1] = TeddyBear[1] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][1]
                TeddyBear_tmp_avg[2] = TeddyBear[2] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][2]
            # TeddyBear_tmp_avg[0] = TeddyBear[0] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][0]
            # TeddyBear_tmp_avg[1] = TeddyBear[1] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][1]
            # TeddyBear_tmp_avg[2] = TeddyBear[2] * (len(TeddyBear_avg) - 1) + TeddyBear_avg[len(TeddyBear_avg) - 1][2]
            x_avg = TeddyBear_tmp_avg[0] / len(TeddyBear_avg)
            y_avg = TeddyBear_tmp_avg[1] / len(TeddyBear_avg)
            z_avg = TeddyBear_tmp_avg[2] / len(TeddyBear_avg)

            x_error = 100
            y_error = 100
            z_error = 100
            for i in range(len(TeddyBear_avg)):
                tmp_x_error = np.sqrt(pow((TeddyBear_avg[i][0] - x_avg), 2))
                tmp_y_error = np.sqrt(pow((TeddyBear_avg[i][1] - y_avg), 2))
                tmp_z_error = np.sqrt(pow((TeddyBear_avg[i][2] - z_avg), 2))
                if tmp_x_error < x_error:
                    x_error = tmp_x_error
                    TeddyBear[0] = TeddyBear_avg[i][0]
                if tmp_y_error < y_error:
                    y_error = tmp_y_error
                    TeddyBear[1] = TeddyBear_avg[i][1]
                if tmp_z_error < z_error:
                    z_error = tmp_z_error
                    TeddyBear[2] = TeddyBear_avg[i][2]
            print('TeddyBear: ', TeddyBear[0], TeddyBear[1], TeddyBear[2])

        if len(Chair_avg) >= 3: # !=0
            Chair[0] = 0
            Chair[1] = 0
            Chair[2] = 0
            for i in range(3):
                Chair[0] = Chair[0] + Chair_avg[-i-1][0]
                Chair[1] = Chair[1] + Chair_avg[-i-1][1]
                Chair[2] = Chair[2] + Chair_avg[-i-1][2]
            
            Chair[0] = Chair[0] / 3.0
            Chair[1] = Chair[1] / 3.0
            Chair[2] = Chair[2] / 3.0
            
            # Chair[0] = Chair_avg[len(Chair_avg) - 1][0]
            # Chair[1] = Chair_avg[len(Chair_avg) - 1][1]
            # Chair[2] = Chair_avg[len(Chair_avg) - 1][2]
            print('Chair: ', Chair[0], Chair[1], Chair[2])

        submission_path = os.path.realpath('..')
        file = open(submission_path+'/output/drone_output.txt', 'w')
        for element in List:
            file.write(str(element[0]) + " ")
            file.write(str(element[1]) + " ")
            file.write(str(element[2]) + "\n")
        file.close()

def publish_object_location(object_position, depth_img, org, object):
    # print(object_position/1000)
    point_message = PointStamped()
    point_message.header = depth_img.header
    point_message.header.frame_id = "origin"
    point_message.point.x = object_position[0]/1000 + org[0]
    point_message.point.y = object_position[1]/1000 + org[1]
    point_message.point.z = object_position[2]/1000 + org[2]
    object.append((point_message.point.x, point_message.point.y, point_message.point.z))
    # print(obj[0], obj[1], obj[2])
    pub.publish(point_message)

def getXYZ(xp, yp, zc, fx, fy, cx, cy):
    #### Definition:
    # cx, cy : image center(pixel)
    # fx, fy : focal length
    # xp, yp: index of the depth image
    # zc: depth
    inv_fx = 1.0/fx
    inv_fy = 1.0/fy
    x = (xp-cx) *  zc * inv_fx
    y = (yp-cy) *  zc * inv_fy
    z = zc
    return (x,y,z,1.0)

if __name__ == '__main__':
    main()
