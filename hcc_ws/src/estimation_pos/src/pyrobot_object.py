#!/usr/bin/env python2

from numpy.lib import append
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
from tf.transformations import quaternion_matrix
import math
import os
import sys

pub = rospy.Publisher('/object_pose', PointStamped, queue_size=10)
pub1 = rospy.Publisher('/camera_pose', PointStamped, queue_size=10)
pub2 = rospy.Publisher('/gt_pose', PointStamped, queue_size=10)
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

print('try to get tag1')
listener = tf.TransformListener()
listener.waitForTransform( '/origin', '/map_tag_1',rospy.Time.now(), rospy.Duration(10.0))
(trans, rot) = listener.lookupTransform('/origin', '/map_tag_1', rospy.Time.now())
print(trans)
print(rot)
tag1_transform = quaternion_matrix(np.array([rot[0],rot[1],rot[2],rot[3]])) #(???)
tag1_transform[0][3] = trans[0] #???
tag1_transform[1][3] = trans[1] #???
tag1_transform[2][3] = trans[2] #???
v1 = np.array([0,0,0,1])
tag_1 = np.matmul(tag1_transform, v1)
submission_path = os.path.realpath('..') + "/output/tag1"
np.save(submission_path ,tag_1)
print('get tag1')

transform_time = 0.0
transform = Odometry()

dis_tag1=10000

Orange_bottle = np.zeros(3)
Green_bottle = np.zeros(3)
Laptop_near_tag1 =  np.zeros(3)
Backpack = np.zeros(3)
TeddyBear = np.zeros(3)

Orange_bottle_output = np.array([])
Green_bottle_output = np.array([])
Laptop_output = np.array([])
Backpack_output = np.array([])
TeddyBear_output = np.array([])


def main():
    depth_image_sub = message_filters.Subscriber('/camera/aligned_depth_to_color/image_raw', Image) # ('???', ???)
    ## Note that you may need color image to find the color of bottles
    color_image_sub = message_filters.Subscriber('/camera/color/image_raw', Image) #('???', ???)
    bb_sub = message_filters.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes) #('???', ???)
    ts = message_filters.ApproximateTimeSynchronizer([depth_image_sub, bb_sub, color_image_sub], 10, 0.5) #(???, ???, ???)
    ts.registerCallback(callback)
    rospy.Subscriber("apriltag_localization", Odometry, transform_cb) #("???", ???, ???)
    rospy.spin()

def transform_cb(msg):
    global transform_time
    global transform
    transform_time = msg.header.stamp.to_sec()
    transform = msg
    # print("Get transform time")
    # print(transform_time)

def publish_object_location(object_position, depth_img, org, obj, class_type, bb_size):
    global Orange_bottle_output
    global Green_bottle_output
    global Laptop_output
    global Backpack_output
    global TeddyBear_output
    # print(object_position/1000)
    point_message = PointStamped()
    point_message.header = depth_img.header
    point_message.header.frame_id = "origin"
    point_message.point.x = object_position[0]/1000 + org[0]
    point_message.point.y = object_position[1]/1000 + org[1]
    point_message.point.z = object_position[2]/1000 + org[2]
    # update obj
    obj[0] = object_position[0]/1000 + org[0]
    obj[1] = object_position[1]/1000 + org[1]
    obj[2] = object_position[2]/1000 + org[2]
    # append to array
    if class_type == "ob":
        Orange_bottle_output = np.append(Orange_bottle_output,obj)
    elif class_type == "gb":
        Green_bottle_output = np.append(Green_bottle_output,obj)
    elif class_type == "lap":
        Laptop_output = np.append(Laptop_output,obj)
    elif class_type == "bp":
        Backpack_output = np.append(Backpack_output,obj)
        pub.publish(point_message)
    elif class_type == "tb":
        TeddyBear_output = np.append(TeddyBear_output,obj)
    # print(Green_bottle_output.reshape(-1,3))
    # usage: reshape(-1,3) --> [[o,o,o][o,o,o][o,o,o]]
    submission_path = os.path.realpath('..') + "/output/p"
    np.savez(submission_path ,a=Orange_bottle_output,b=Green_bottle_output,c=Laptop_output,d=Backpack_output,e=TeddyBear_output)
    # print("npsave {0}",class_type)


def callback(depth_img, bb, color_img):
    global transform_time
    global transform
    local_time = depth_img.header.stamp.to_sec()
    print("Get local_time")
    print(local_time)
    print(transform_time)
    # you could set the time error (local_time - transform_time) by yourself    
    if abs(local_time - transform_time) < 1 and transform_time != 0: #??? and transform_time != 0:
        global tag_1
        print("Time error")

        # hint: http://docs.ros.org/en/jade/api/tf/html/python/transformations.html
        # You could use "quaternion_matrix" function to find the 4x4 transform matrix
        print(local_time - transform_time)
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
            cv_colorimage = cv_bridge.imgmsg_to_cv2(color_img, "rgb8")
            cv_colorimage2 = np.array(cv_colorimage, dtype=np.float32)
        except CvBridgeError as e:
            print(e)
        # publish camera pos in origin frame
        v1 = np.array([0,0,0,1])
        org = np.matmul(global_transform, v1)
        # org = [0.6,1.804,0.14]
        # print("camera_link")
        # print(object_position)
        point_message = PointStamped()
        point_message.header = depth_img.header
        point_message.header.frame_id = "origin"
        point_message.point.x = org[0]
        point_message.point.y = org[1]
        point_message.point.z = org[2]
        pub1.publish(point_message)
        print("pub camera")

        # put the ground truth here for rviz
        # point_message.point.x = 0
        # point_message.point.y = 3.924
        # point_message.point.z = 0.17
        # pub2.publish(point_message)

        for i in bb.bounding_boxes:
            x_mean = (i.xmax + i.xmin) / 2
            y_mean = (i.ymax + i.ymin) / 2
            bb_size = (i.xmax - i.xmin)*(i.ymax - i.ymin)
            thr = 20
            if i.xmax>(640-thr) or i.xmin<thr or i.ymax>(480-thr) or i.ymin<thr:
                continue
            # print(i) xmax:640 ymax:480

            if i.Class == "bottle" and i.probability>0.30:
                zc = cv_depthimage2[int(y_mean)+10][int(x_mean)]
                color = cv_colorimage2[int(y_mean)][int(x_mean)]
                if color[0] > color[1]: 
                    # more red than green is OOOOOOrange
                    rospy.loginfo("see orange bottle")
                    v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                    object_position = np.dot(global_transform, v1)
                    # if 0.3 < dist3d(object_position[0]/1000-Orange_bottle[0], object_position[1]/1000-Orange_bottle[1], object_position[2]/1000-Orange_bottle[2]) :
                    publish_object_location(object_position,depth_img, org, Orange_bottle, "ob", bb_size)
                elif color[0] < color[1]:
                    rospy.loginfo("see green bottle")
                    v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                    object_position = np.dot(global_transform, v1)
                    # if 0.3 < dist3d(object_position[0]/1000-Orange_bottle[0], object_position[1]/1000-Orange_bottle[1], object_position[2]/1000-Orange_bottle[2]) :
                    publish_object_location(object_position,depth_img, org, Green_bottle, "gb", bb_size)
            
            elif (i.Class == "laptop" or i.Class == "tvmonitor") and i.probability>0.4:
                rospy.loginfo("see laptop")
                zc = cv_depthimage2[int(y_mean+20)][int(x_mean)]
                v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                object_position = np.dot(global_transform, v1)
                # print('dis from tag1')
                # d = math.sqrt((tag_1[0]-object_position[0]/1000)*(tag_1[0]-object_position[0]/1000) + (tag_1[1]-object_position[1]/1000)*(tag_1[1]-object_position[1]/1000)+(tag_1[2]-object_position[2]/1000)*(tag_1[2]-object_position[2]/1000))
                # print(d)
                # if 0.3 < dist3d(object_position[0]/1000-Laptop_near_tag1[0], object_position[1]/1000-Laptop_near_tag1[1], object_position[2]/1000-Laptop_near_tag1[2]) :
                publish_object_location(object_position,depth_img, org, Laptop_near_tag1, "lap", bb_size)

            elif i.Class == "backpack" and i.probability>0.1:
                rospy.loginfo("see backpack")
                zc = cv_depthimage2[int(y_mean)][int(x_mean)]
                v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                object_position = np.dot(global_transform, v1)
                # if 0.3 < dist3d(object_position[0]/1000-Backpack[0], object_position[1]/1000-Backpack[1], object_position[2]/1000-Backpack[2]) :
                publish_object_location(object_position,depth_img, org, Backpack, "bp", bb_size)

            elif i.Class == "teddy bear" and i.probability>0.08:
                rospy.loginfo("see teddy bear")
                zc = cv_depthimage2[int(y_mean)][int(x_mean)]
                v1 = np.array(getXYZ(x_mean, y_mean, zc, fx, fy, cx, cy))
                object_position = np.dot(global_transform, v1)
                # if 0.3 < dist3d(object_position[0]/1000-TeddyBear[0], object_position[1]/1000-TeddyBear[1], object_position[2]/1000-TeddyBear[2]) :
                publish_object_location(object_position,depth_img, org, TeddyBear, "tb", bb_size)

            ############################
            #  Student Implementation  #
            ############################
            # print ("os.path.realpath(__file__) = ", os.path.realpath('..'))
            # Write in .txt
            #list = [Orange_bottle, Green_bottle, Laptop_near_tag1, Backpack, TeddyBear]
            #submission_path = os.path.realpath('..')
            #file = open(submission_path+'/output/pyrobot_output.txt', 'w')
            #for element in list:
            #    file.write(str(element[0]) + " ")
            #    file.write(str(element[1]) + " ")
            #    file.write(str(element[2]) + "\n")
            #file.close()

            

def getXYZ(xp, yp, zc, fx,fy,cx,cy):
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
    return (x,y,z,1)

def dist3d(a,b,c):
    return math.sqrt(a*a + b*b + c*c)


if __name__ == '__main__':
    main()
