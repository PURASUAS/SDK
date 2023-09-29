import asyncio
from mavsdk import System


async def print_flight_mode():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

   
    print(1)
    await drone.action.set_return_to_launch_altitude(0)  
    print(1)

    await drone.action.set_flight_mode("STABILIZE")

    print("Flight mode changed to STABILIZE")

    async for flight_mode in drone.telemetry.flight_mode():
        print("FlightMode:", flight_mode)
    



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_flight_mode())
