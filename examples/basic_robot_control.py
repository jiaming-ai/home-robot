import time

import numpy as np

from home_robot.motion.stretch import STRETCH_HOME_Q, HelloStretchKinematics
from home_robot_hw.stretch_client import StretchClient

if __name__ == "__main__":
    robot = StretchClient()
    model = HelloStretchKinematics()

    # Acquire camera observations
    imgs = robot.head.get_images()

    # Get camera pose
    camera_pose = robot.head.get_pose()
    print(f"camera_pose={camera_pose}")

    # Move camera
    robot.head.set_pan_tilt(pan=np.pi / 4, tilt=-np.pi / 3, blocking=True)
    robot.head.look_at_ee(blocking=True)
    robot.head.look_ahead()

    # Switch to navigation mode
    robot.switch_to_navigation_mode()
    assert robot.in_navigation_mode()

    # Get base pose
    xyt = robot.nav.get_base_pose()
    print(f"xyt={xyt}")

    # Command robot velocities
    robot.nav.set_velocity(v=0.2, w=0.0)
    time.sleep(2)
    robot.nav.set_velocity(v=0.0, w=0.0)

    # Command the robot to navigate to a waypoint
    xyt_goal = [0.15, 0.15, -np.pi / 4]
    robot.nav.navigate_to(xyt_goal, blocking=True)

    # Home robot base (navigate back to origin)
    robot.nav.home()

    # Switch to manipulation mode
    robot.switch_to_manipulation_mode()
    assert robot.in_manipulation_mode()

    # Home robot joints (moves to predefined home joint configuration)
    robot.manip.home()

    # Command the robot arm 1
    q_desired = np.array([-0.1, 0.5, 0.3, 0, 0, 0])
    robot.manip.goto_joint_positions(q_desired, blocking=True)

    pos_desired = np.array([0.2, -0.2, 0.4])
    quat_desired = np.array([-0.7079143, 0.12421559, 0.1409881, -0.68084526])
    robot.manip.goto_ee_pose(pos_desired, quat_desired, blocking=True)

    # Command the robot arm 2
    robot.manip.goto(STRETCH_HOME_Q)

    # Gripper commands
    robot.manip.open_gripper(blocking=True)
    robot.manip.close_gripper()

    # Test command in wrong mode
    assert robot.in_manipulation_mode()
    try:
        robot.nav.navigate_to()
    except TypeError:
        pass  # prints out an rospy.logerr that alerts the user of erroneous mode

    # Some commands are still available
    xyt = robot.nav.get_base_pose()
    print(f"xyt={xyt}")

    # Stop all robot motion
    robot.stop()