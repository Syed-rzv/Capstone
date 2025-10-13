# classifier_service.py
"""
ML Classifier service for emergency call classification.
Provides both main type classification (EMS/Fire/Traffic) and 
cascading subtype classification.
"""
import joblib
import os


class EmergencyClassifier:
    """Loads XGBoost model and provides prediction interface."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
            model_path = os.path.join(base_dir, 'models', 'XGBoost_Combined_MultiJurisdiction.pkl')
        
        self.model_path = model_path
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk."""
        try:
            print(f"Loading main classifier from: {self.model_path}")
            model_bundle = joblib.load(self.model_path)
            
            if isinstance(model_bundle, dict):
                self.model = model_bundle.get('model')
                self.vectorizer = model_bundle.get('vect')
                self.label_encoder = model_bundle.get('label_encoder')
            else:
                self.model = model_bundle
            
            print(f"✅ Main classifier loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading main classifier: {str(e)}")
            raise
    
    def predict(self, text):
        """Predict emergency type from call description."""
        if not self.model or not self.vectorizer:
            raise Exception("Model not loaded properly")
        
        # Vectorize text
        text_vec = self.vectorizer.transform([text])
        
        # Predict
        prediction_encoded = self.model.predict(text_vec)[0]
        
        # Decode label
        if self.label_encoder:
            prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        else:
            prediction = prediction_encoded
        
        return prediction


class SubtypeClassifier:
    """Loads subtype classifiers for EMS, Fire, and Traffic."""
    
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
        models_dir = os.path.join(base_dir, 'models')
        
        self.classifiers = {}
        
        # Load all three subtype models
        for emergency_type in ['EMS', 'Fire', 'Traffic']:
            model_path = os.path.join(models_dir, f'XGBoost_{emergency_type}_Subtype.pkl')
            self.classifiers[emergency_type] = self._load_model(model_path, emergency_type)
    
    def _load_model(self, model_path, emergency_type):
        """Load a single subtype model."""
        try:
            print(f"Loading {emergency_type} subtype classifier from: {model_path}")
            model_bundle = joblib.load(model_path)
            
            if isinstance(model_bundle, dict):
                classifier = {
                    'model': model_bundle.get('model'),
                    'vectorizer': model_bundle.get('vect'),
                    'label_encoder': model_bundle.get('label_encoder')
                }
            else:
                classifier = {'model': model_bundle}
            
            print(f"✅ {emergency_type} subtype classifier loaded")
            return classifier
            
        except Exception as e:
            print(f"❌ Error loading {emergency_type} subtype classifier: {str(e)}")
            return None
    
    def predict(self, text, emergency_type):
        """Predict subtype based on main emergency type."""
        if emergency_type not in self.classifiers:
            print(f"⚠️  No subtype classifier for {emergency_type}")
            return "Unknown"
        
        classifier = self.classifiers[emergency_type]
        
        if not classifier or not classifier.get('model'):
            print(f"⚠️  {emergency_type} classifier not loaded properly")
            return "Unknown"
        
        try:
            # Vectorize text
            text_vec = classifier['vectorizer'].transform([text])
            
            # Predict
            prediction_encoded = classifier['model'].predict(text_vec)[0]
            
            # Decode label
            if classifier.get('label_encoder'):
                prediction = classifier['label_encoder'].inverse_transform([prediction_encoded])[0]
            else:
                prediction = prediction_encoded
            
            return prediction
            
        except Exception as e:
            print(f"❌ Error predicting {emergency_type} subtype: {str(e)}")
            return "Unknown"


# Global instances (loaded once when module imports)
_main_classifier = None
_subtype_classifier = None


def classify_call(description):
    """
    Classify emergency call into main type (EMS/Fire/Traffic).
    
    Args:
        description (str): Emergency call description
        
    Returns:
        str: Emergency type ('EMS', 'Fire', or 'Traffic')
    """
    global _main_classifier
    
    if _main_classifier is None:
        _main_classifier = EmergencyClassifier()
    
    return _main_classifier.predict(description)


def classify_subtype(description, emergency_type):
    """
    Classify emergency call into specific subtype using cascading classifier.
    
    Args:
        description (str): Emergency call description
        emergency_type (str): Main emergency type ('EMS', 'Fire', or 'Traffic')
        
    Returns:
        str: Emergency subtype
    """
    global _subtype_classifier
    
    if _subtype_classifier is None:
        _subtype_classifier = SubtypeClassifier()
    
    return _subtype_classifier.predict(description, emergency_type)