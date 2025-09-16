from config import setup_config
from infrastructure.grpc.channel_manager import (
    GRPCChannelManager,
    GRPCServiceConfig,
)


def init_grpc_services():
    config = setup_config().inventory

    GRPCChannelManager.register_service(
        "inventory",
        GRPCServiceConfig(
            url=config.grpc_url,
            service_name="inventory",
            options=[
                ("grpc.keepalive_time_ms", 30_000),
                ("grpc.keepalive_timeout_ms", 15_000),
                ("grpc.http2.max_pings_without_data", 5),
                ("grpc.keepalive_permit_without_calls", 1),
            ],
        ),
    )


async def cleanup_grpc_services():
    manager = GRPCChannelManager.get_instance()
    await manager.close_all_channels()
    print("Closed gRPC all channels.")
