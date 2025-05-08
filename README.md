Check presentation: https://www.canva.com/design/DAGHMAv3eP0/5nI3x9QHzviZlslpe4ANdw/view?utm_content=DAGHMAv3eP0&utm_campaign=designshare&utm_medium=link&utm_source=editor

# Smart Farm: Plant Disease Detection Platform


## 📋 Overview

Smart Farm is a web application designed to help farmers, botanists, and agricultural researchers diagnose plant diseases by uploading leaf images. Using deep learning techniques, the platform accurately identifies plant diseases and provides detailed information about causes, symptoms, and treatment options.

## 🌱 Project Objectives

- **Improve Disease Diagnosis Accuracy**: Leverage deep learning models to provide accurate disease detection
- **Offer an Economical Solution**: Create an accessible alternative to expensive agricultural diagnostic systems
- **User-Friendly Interface**: Develop an intuitive platform that can be used by experts and non-experts alike
- **All-in-One Solution**: Combine disease detection, informational database, and community features

## 🔍 Features

- **Disease Detection**: Upload leaf images to diagnose plant diseases
- **User Accounts**: Register and manage personal profiles
- **Community Forum**: Share experiences and get advice from other users
- **Disease Information Database**: Access comprehensive information about plant diseases
- **Chatbot Assistance**: Get help navigating the platform
- **Contact System**: Reach out to site administrators

## 🧠 Technologies Used

### Backend
- **Language**: Python
- **Framework**: Flask
- **Database**: MySQL
- **ORM**: SQLAlchemy

### Machine Learning
- **Dataset**: PlantVillage dataset from Kaggle (by Sharada P. Mohanty)
- **Models**: 
  - General plant disease model (97% accuracy)
  - Plant-specific models:
    - Apple disease model (99% accuracy)
    - Corn disease model (96% accuracy)
    - Grapes disease model (99% accuracy)
    - Potato disease model (100% accuracy)
    - Tomato disease model (94% accuracy)
- **Training Parameters**:
  - Optimizer: Adam (learning rate: 0.0001)
  - Loss Function: Categorical Cross-Entropy
  - General Model: 10 epochs
  - Specific Models: 20 epochs

## 🛠️ System Architecture

The system follows a modular architecture with:
- Frontend interface for image upload and result display
- Backend API for processing requests and database management
- Deep learning models for disease classification
- Community features with real-time communication

## 📊 Model Performance

| Model   | Accuracy |
|---------|----------|
| Apple   | 99%      |
| Corn    | 96%      |
| Grapes  | 99%      |
| Potato  | 100%     |
| Tomato  | 94%      |
| General | 97%      |

## 🔄 Getting Started

### Prerequisites
- Python 3.x
- Flask
- TensorFlow
- MySQL
- Required Python packages (see requirements.txt)

### Installation

1. Clone the repository
```bash
git clone https://github.com/username/smart-farm.git
cd smart-farm
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up the database
```bash
python setup_database.py
```

4. Run the application
```bash
python app.py
```

5. Access the application at `http://localhost:5000`

## 📱 User Interfaces

The platform includes interfaces for:
- Image upload for disease detection
- Disease prediction results display with probability scores
- Community forum for user discussions
- User account management

## 🔮 Future Perspectives

- **E-commerce Integration**: Offer treatment products based on diagnosed diseases
- **Enhanced User Interface**: Improve usability and visual appeal
- **Mobile Application**: Develop a dedicated mobile version
- **Expanded Disease Database**: Add more plant species and disease classes

## 👥 Contributors

- **Elhadj Asma** - Project Developer
- **Mme. Taktak Hajer** - Project Supervisor

