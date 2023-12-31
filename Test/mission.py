#!/usr/bin/env python3

import asyncio
from geopy.distance import geodesic
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)


async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(
        print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(
        observe_is_in_air(drone, running_tasks))


    original_latitude=0
    original_longitude=0
    async for position in drone.telemetry.position():
        # Only need position once
        if position.latitude_deg and position.longitude_deg:
            original_latitude = position.latitude_deg
            original_longitude = position.longitude_deg
            break
            
    

    displacement = (10, 10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    new_latitude = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    new_longitude = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))


    mission_items = []
    mission_items.append(MissionItem(new_latitude,
                                     new_longitude,
                                     25,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan')))
    

    displacement = (-10, 10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    new_latitude = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    new_longitude = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))


    mission_items.append(MissionItem(new_latitude,
                                     new_longitude,
                                     25,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan')))

    displacement = (-10, -10)

    # Create a geodesic object with the original coordinates
    original_location = (original_latitude, original_longitude)
    new_latitude = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    new_longitude = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))




    mission_items.append(MissionItem(new_latitude,
                                     new_longitude,
                                     25,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan')))

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task


async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
