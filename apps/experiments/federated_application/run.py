from src.app.adapted import SessionWandbLogger
from src.app.federated_app import FederatedApp
from src.app.settings import Settings
from src.federated.subscribers.wandb_logger import WandbLogger

config = Settings.from_json_file('./config.json')
if __name__ == '__main__':
    app = FederatedApp(config)
    app.start_all()
