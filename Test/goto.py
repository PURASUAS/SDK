from geopy.distance import geodesic
import asyncio
from mavsdk import System


async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev//ttyACM0")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break

    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(1)
    # To fly drone 20m above the ground plane
    flying_alt = absolute_altitude + 10.0


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
    new_latitude = original_latitude + (displacement[0] / 111.32)  # Approximately 111.32 km per degree of latitude
    new_longitude = original_longitude + (displacement[1] / (111.32 * abs(geodesic(original_location, (original_latitude, original_longitude + 1)).meters)))



    # goto_location() takes Absolute MSL altitude
    await drone.action.goto_location(new_latitude, new_longitude, flying_alt, 0)

    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
