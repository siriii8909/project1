import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import MobileNetV2
import os
import numpy as np
from PIL import Image

# Define a comprehensive list of plants and diseases
CLASSES = [
    'Apple - Apple Scab', 'Apple - Black Rot', 'Apple - Cedar Apple Rust', 'Apple - Healthy',
    'Blueberry - Healthy',
    'Cherry - Powdery Mildew', 'Cherry - Healthy',
    'Corn - Cercospora Leaf Spot', 'Corn - Common Rust', 'Corn - Northern Leaf Blight', 'Corn - Healthy',
    'Grape - Black Rot', 'Grape - Esca (Black Measles)', 'Grape - Leaf Blight', 'Grape - Healthy',
    'Orange - Haunglongbing (Citrus Greening)',
    'Peach - Bacterial Spot', 'Peach - Healthy',
    'Pepper - Bacterial Spot', 'Pepper - Healthy',
    'Potato - Early Blight', 'Potato - Late Blight', 'Potato - Healthy',
    'Raspberry - Healthy',
    'Rice - Brown Spot', 'Rice - Hispa', 'Rice - Leaf Blast', 'Rice - Healthy',
    'Soybean - Healthy',
    'Squash - Powdery Mildew',
    'Strawberry - Leaf Scorch', 'Strawberry - Healthy',
    'Tomato - Bacterial Spot', 'Tomato - Early Blight', 'Tomato - Late Blight', 'Tomato - Leaf Mold',
    'Tomato - Septoria Leaf Spot', 'Tomato - Spider Mites', 'Tomato - Target Spot',
    'Tomato - Yellow Leaf Curl Virus', 'Tomato - Mosaic Virus', 'Tomato - Healthy',
    'Wheat - Yellow Rust', 'Wheat - Septoria', 'Wheat - Healthy'
]
DATASET_DIR = 'dataset'
MODEL_PATH = 'crop_model.h5'

def create_dummy_dataset():
    """Creates a dummy dataset for demonstration if no real data is provided."""
    print(f"Creating a dummy dataset in '{DATASET_DIR}'...")
    os.makedirs(DATASET_DIR, exist_ok=True)
    colors = [(0, 255, 0), (200, 50, 50), (150, 150, 50), (200, 200, 50), (50, 200, 50)]
    for idx, class_name in enumerate(CLASSES):
        class_dir = os.path.join(DATASET_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
        # Create 20 dummy images per class
        for i in range(20):
            img_array = np.zeros((224, 224, 3), dtype=np.uint8)
            img_array[:] = colors[idx]
            # Add some random noise
            noise = np.random.randint(0, 50, (224, 224, 3), dtype=np.uint8)
            img_array = np.clip(img_array + noise, 0, 255)
            img = Image.fromarray(img_array)
            img.save(os.path.join(class_dir, f'dummy_{i}.jpg'))
    print("Dummy dataset created successfully!")

def build_model(num_classes):
    """Builds a high-accuracy model using Transfer Learning with MobileNetV2."""
    base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base_model.trainable = False  # Freeze the base model for initial training

    # Data Augmentation layer to prevent overfitting
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ], name='data_augmentation')

    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = tf.keras.Model(inputs, outputs)
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

def train_model():
    """Trains the model perfectly on the dataset."""
    if not os.path.exists(DATASET_DIR) or len(os.listdir(DATASET_DIR)) < len(CLASSES):
        print("Real dataset not found. Generating dummy dataset for testing...")
        create_dummy_dataset()
    else:
        print("Found real dataset. Starting training...")

    # Load dataset
    print("Loading dataset...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=32,
        label_mode='categorical',
        class_names=CLASSES
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=32,
        label_mode='categorical',
        class_names=CLASSES
    )

    # Normalize data (0 to 1) to match predictor.py
    normalization_layer = tf.keras.layers.Rescaling(1./255)
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # Prefetch for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # Build model
    model = build_model(len(CLASSES))

    # Callbacks
    checkpoint = callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_accuracy', mode='max')
    early_stop = callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    reduce_lr = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-5)

    print("Starting training...")
    epochs = 20  # Train perfectly
    
    # Train the top layers
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=[checkpoint, early_stop, reduce_lr]
    )

    print(f"Training complete! Best model saved to {MODEL_PATH}")
    print("\nIMPORTANT: If you used the dummy dataset, the model will only detect colors.")
    print("To train perfectly on real crops:")
    print("1. Delete the 'dataset' folder.")
    print("2. Create 'dataset' folder and add 5 folders inside it named exactly:")
    for c in CLASSES:
        print(f"   - {c}")
    print("3. Put real images of the crops into their respective folders.")
    print("4. Run `python train_model.py` again.")

if __name__ == "__main__":
    train_model()
