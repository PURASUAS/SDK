#!/usr/bin/env python3

#This example shows how to use the follow me plugin
from geopy.distance import geodesic
import asyncio
from mavsdk import System
from mavsdk.follow_me import (Config, FollowMeError, TargetLocation)

default_height = 8.0 #in Meters
follow_distance = 2.0 #in Meters, this is the distance that the drone will remain away from Target while following it
#Direction relative to the Target
#Options are NONE, FRONT, FRONT_LEFT, FRONT_RIGHT, BEHIND
direction = Config.FollowDirection.BEHIND
responsiveness =  0.02




async def fly_drone():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    #Arming the drone
    print ("-- Arming")
    await drone.action.arm()

    #Follow me Mode requires some configuration to be done before starting the mode
    conf = Config(default_height, follow_distance, direction, responsiveness)
    await drone.follow_me.set_config(conf)

    print ("-- Taking Off")
    await drone.action.takeoff()
    await asyncio.sleep(8)
    print ("-- Starting Follow Me Mode")
    await drone.follow_me.start()
    await asyncio.sleep(8)





    original_latitude=0
    original_longitude=0
    async for position in drone.telemetry.position():
        # Only need position once
        if position.latitude_deg and position.longitude_deg:
            original_latitude = position.latitude_deg
            original_longitude = position.longitude_deg
            break

    # Define the displacement in meters (10 meters north and 10 meters east)
    displacement = (10, 10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    lat1 = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    lon1 = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))

    displacement = (-10, 10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    lat2 = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    lon2 = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))


    displacement = (10, -10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    lat3 = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    lon3 = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))



    fake_location  =[[lat1,lon1],[lat2,lon2],[lat3,lon3]] 




    #This for loop provides fake coordinates from the fake_location list for the follow me mode to work
    #In a simulator it won't make much sense though
    for latitude,longitude in fake_location:
        target = TargetLocation(latitude, longitude, 0, 0, 0, 0)
        print ("-- Following Target")
        await drone.follow_me.set_target_location(target)
        await asyncio.sleep(2)

    #Stopping the follow me mode
    print ("-- Stopping Follow Me Mode")
    await drone.follow_me.stop()
    await asyncio.sleep(5)

    print ("-- Landing")
    await drone.action.land()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fly_drone())
