# ASL Dataset Download Options

## ✅ RECOMMENDED: Kaggle ASL Image Dataset
**Much smaller than WLASL videos!**
- Size: ~100-200 MB (vs 50+ GB for WLASL videos)
- Type: Images (easier to work with)
- Link: https://kaggle.com/datasets/ayuraj/asl-dataset

### Quick Setup:

**Method 1: Kaggle API (Automated)**
```powershell
# Run the download script
.venv\Scripts\python.exe download_kaggle_dataset.py
```

**Method 2: Manual Browser Download**
1. Visit: https://kaggle.com/datasets/ayuraj/asl-dataset
2. Click "Download" button (sign in required)
3. Extract to: `kaggle_asl_dataset/` folder
4. Done!

---

## 🌐 Other Lightweight ASL Datasets

### 1. **ASL Alphabet (Smallest - 87 MB)**
- Link: https://www.kaggle.com/datasets/grassknoted/asl-alphabet
- Content: A-Z alphabet signs + space, delete, nothing
- Classes: 29 categories
- Images: ~87,000 images
- Best for: Quick testing and demos

### 2. **ASL MNIST (Tiny - 34 MB)**
- Link: https://www.kaggle.com/datasets/datamunge/sign-language-mnist
- Content: A-Z alphabet (static signs only)
- Classes: 24 letters (J and Z excluded - require motion)
- Format: CSV files
- Best for: Quick training and testing

### 3. **MediaPipe ASL Dataset (Google)**
- Link: https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer
- Content: Hand landmarks dataset
- Type: Real-time gesture recognition
- Best for: Live webcam integration

---

## 🎯 RECOMMENDED WORKFLOW

### For Your Voice-to-Sign Project:

**Option A: Image-Based (Easiest)**
1. Download Kaggle ASL Alphabet dataset
2. Use images instead of videos
3. Display sequence of images for words
4. Much faster and lighter!

**Option B: Cloud-Based (No local storage)**
1. Use Google Colab or Kaggle Notebooks
2. Train model in cloud
3. Download only the trained model
4. Use model locally for inference

**Option C: Streaming (No download)**
1. Use pre-trained models via API
2. Google MediaPipe for hand detection
3. TensorFlow Hub for ASL recognition
4. Real-time webcam interpretation

---

## 💡 INTEGRATION STEPS

### Step 1: Download Lightweight Dataset
```powershell
# Option 1: Run our script
.venv\Scripts\python.exe download_kaggle_dataset.py

# Option 2: Install kaggle CLI
pip install kaggle
kaggle datasets download -d ayuraj/asl-dataset
unzip asl-dataset.zip -d kaggle_asl_dataset
```

### Step 2: Adapt Your Code
We'll modify `translate_sentence.py` to use:
- Images instead of videos (faster)
- Image sequences for words
- Optional: GIF generation for smoother output

### Step 3: Test
```powershell
.venv\Scripts\python.exe vosk_demo.py
```

---

## ⚡ QUICK START (Recommended)

**Fastest way to test without heavy downloads:**

1. Use the Kaggle browser download (1 click)
2. Extract to project folder
3. I'll adapt the code to use images
4. Start converting voice to sign!

**Want me to set this up for you?** Just let me know which dataset you prefer!
