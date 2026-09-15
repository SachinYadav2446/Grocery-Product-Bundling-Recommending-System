from pathlib import Path

# Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = BASE_DIR / "saved_models"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Hugging Face Mirror Base URL for Instacart
HF_DATASET_URL = "https://huggingface.co/datasets/attik/Instacart-Market-Basket-Analysis/resolve/main"

FILES_TO_DOWNLOAD = [
    "departments.csv",
    "aisles.csv",
    "products.csv",
    "orders.csv",
    "order_products__train.csv",
]

# Model Hyperparameters
USER_EMBEDDING_DIM = 64
ITEM_EMBEDDING_DIM = 64
AISLE_EMBEDDING_DIM = 32
DEPT_EMBEDDING_DIM = 16
OUTPUT_EMBEDDING_DIM = 64

LEARNING_RATE = 0.001
BATCH_SIZE = 512
NUM_EPOCHS = 8
TEMPERATURE = 0.07

# Business & Inference Settings
TOP_K_CANDIDATES = 100
FINAL_RECOMMENDATIONS_COUNT = 10
MAX_ITEMS_PER_AISLE = 2  # Diversity constraint
