#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Make Cozmo drive towards his charger.

The script shows an example of accessing the charger object from
Cozmo's world, and driving towards it.
'''

import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps


def drive_to_charger(robot):
    '''The core of the drive_to_charger program'''

    # If the robot was on the charger, drive them forward and clear of the charger
    if robot.is_on_charger:
        # drive off the charger
        robot.drive_off_charger_contacts().wait_for_completed()
        robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()
        # Start moving the lift down
        robot.move_lift(-3)
        # turn around to look at the charger
        robot.turn_in_place(degrees(180)).wait_for_completed()
        # Tilt the head to be level
        robot.set_head_angle(degrees(0)).wait_for_completed()
        # wait half a second to ensure Cozmo has seen the charger
        time.sleep(0.5)
        # drive backwards away from the charger
        robot.drive_straight(distance_mm(-60), speed_mmps(50)).wait_for_completed()

    # try to find the charger
    charger = None

    # see if Cozmo already knows where the charger is
    if robot.world.charger:
        if robot.world.charger.pose.is_comparable(robot.pose):
            print("Cozmo already knows where the charger is!")
            charger = robot.world.charger
        else:
            # Cozmo knows about the charger, but the pose is not based on the
            # same origin as the robot (e.g. the robot was moved since seeing
            # the charger) so try to look for the charger first
            pass

    if not charger:
        # Tell Cozmo to look around for the charger
        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            charger = robot.world.wait_for_observed_charger(timeout=30)
            print("Found charger: %s" % charger)
        except asyncio.TimeoutError:
            print("Didn't see the charger")
        finally:
            # whether we find it or not, we want to stop the behavior
            look_around.stop()

    if charger:
        # Attempt to drive near to the charger, and then stop.
        # Changed to include docking maneuver attempt
        robot.say_text("There you are.").wait_for_completed()
        action = robot.go_to_object(charger, distance_mm(40.0)) # Distance changed, ALIGNMENT NEEDS WORK!
        action.wait_for_completed()
        # Following lines added to turn around and dock with charger
        robot.turn_in_place(degrees(180)).wait_for_completed()
        robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        if robot.is_on_charger:
            robot.say_text("Home sweet home.").wait_for_completed()
        else:
            robot.drive_straight(distance_mm(-50), speed_mmps(50)).wait_for_completed()
            if robot.is_on_charger:
                robot.say_text("Home sweet home.").wait_for_completed()
