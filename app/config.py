import os
from dotenv import load_dotenv

load_dotenv()

# SERVICES
INVENTORY_HOST = os.getenv('INVENTORY_HOST', 'localhost')
INVENTORY_GRPC_PORT = os.getenv('INVENTORY_GRPC_PORT', '50051')