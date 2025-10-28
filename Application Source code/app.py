from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, confusion_matrix
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'regression-analysis-secret-key-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class RegressionAnalyzer:
    def __init__(self):
        pass
    
    def prepare_data(self, df, target_col, feature_cols):
        """Prepare data for modeling"""
        # Check if columns exist
        missing_cols = [col for col in [target_col] + feature_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in data: {missing_cols}")
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Handle missing values
        X = X.fillna(X.mean())
        y = y.fillna(y.mean() if pd.api.types.is_numeric_dtype(y) else y.mode()[0])
        
        return X.values, y.values
    
    def perform_linear_regression(self, df, target_col, feature_cols):
        """Perform linear regression analysis"""
        X, y = self.prepare_data(df, target_col, feature_cols)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Create visualization
        fig = self.create_linear_plot(X_test, y_test, y_pred, feature_cols)
        
        return {
            'r2_score': round(r2, 4),
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'coefficients': model.coef_.tolist(),
            'intercept': round(float(model.intercept_), 4),
            'plot': fig,
            'feature_names': feature_cols
        }
    
    def perform_polynomial_regression(self, df, target_col, feature_cols, degree=2):
        """Perform polynomial regression analysis"""
        X, y = self.prepare_data(df, target_col, feature_cols)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create polynomial features
        poly = PolynomialFeatures(degree=degree)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_poly)
        X_test_scaled = scaler.transform(X_test_poly)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Create visualization
        fig = self.create_polynomial_plot(X_test, y_test, y_pred, feature_cols)
        
        return {
            'r2_score': round(r2, 4),
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'plot': fig,
            'degree': degree,
            'feature_names': feature_cols
        }
    
    def perform_logistic_regression(self, df, target_col, feature_cols):
        """Perform logistic regression analysis"""
        X, y = self.prepare_data(df, target_col, feature_cols)
        
        # Convert to binary if needed
        unique_classes = np.unique(y)
        if len(unique_classes) > 2:
            # Take first two classes for binary classification
            mask = (y == unique_classes[0]) | (y == unique_classes[1])
            X = X[mask]
            y = y[mask]
            unique_classes = np.unique(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # Create visualization
        fig = self.create_logistic_plot(X_test, y_test, y_pred_proba, feature_cols)
        
        return {
            'accuracy': round(accuracy, 4),
            'confusion_matrix': conf_matrix.tolist(),
            'coefficients': model.coef_.tolist(),
            'intercept': model.intercept_.tolist(),
            'plot': fig,
            'feature_names': feature_cols,
            'classes': unique_classes.tolist()
        }
    
    def create_linear_plot(self, X_test, y_test, y_pred, feature_names):
        """Create visualization for linear regression"""
        plt.figure(figsize=(10, 5))
        
        if X_test.shape[1] == 1:
            plt.scatter(X_test, y_test, color='blue', alpha=0.6, label='Actual')
            plt.scatter(X_test, y_pred, color='red', alpha=0.6, label='Predicted')
            plt.xlabel(feature_names[0])
            plt.ylabel('Target')
            plt.legend()
            plt.title('Linear Regression: Actual vs Predicted')
        else:
            residuals = y_test - y_pred
            plt.scatter(y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='red', linestyle='--')
            plt.xlabel('Predicted Values')
            plt.ylabel('Residuals')
            plt.title('Residual Plot')
        
        plt.tight_layout()
        return self.fig_to_base64()
    
    def create_polynomial_plot(self, X_test, y_test, y_pred, feature_names):
        """Create visualization for polynomial regression"""
        plt.figure(figsize=(10, 5))
        
        if X_test.shape[1] == 1:
            # Sort for smooth curve
            sorted_idx = np.argsort(X_test[:, 0])
            X_sorted = X_test[sorted_idx]
            y_pred_sorted = y_pred[sorted_idx]
            
            plt.scatter(X_test, y_test, color='blue', alpha=0.6, label='Actual')
            plt.plot(X_sorted, y_pred_sorted, color='red', linewidth=2, label='Polynomial Fit')
            plt.xlabel(feature_names[0])
            plt.ylabel('Target')
            plt.legend()
            plt.title('Polynomial Regression Fit')
        else:
            residuals = y_test - y_pred
            plt.scatter(y_pred, residuals, alpha=0.6)
            plt.axhline(y=0, color='red', linestyle='--')
            plt.xlabel('Predicted Values')
            plt.ylabel('Residuals')
            plt.title('Residual Plot - Polynomial Regression')
        
        plt.tight_layout()
        return self.fig_to_base64()
    
    def create_logistic_plot(self, X_test, y_test, y_pred_proba, feature_names):
        """Create visualization for logistic regression"""
        plt.figure(figsize=(10, 5))
        
        if X_test.shape[1] == 1:
            # Sort for smooth curve
            sorted_idx = np.argsort(X_test[:, 0])
            X_sorted = X_test[sorted_idx]
            proba_sorted = y_pred_proba[sorted_idx, 1]
            
            plt.scatter(X_test, y_test, color='blue', alpha=0.6, label='Actual')
            plt.plot(X_sorted, proba_sorted, color='red', linewidth=2, label='Probability')
            plt.xlabel(feature_names[0])
            plt.ylabel('Probability/Class')
            plt.legend()
            plt.title('Logistic Regression Probability')
        else:
            plt.hist(y_pred_proba[:, 1], bins=20, alpha=0.7, edgecolor='black')
            plt.xlabel('Predicted Probability')
            plt.ylabel('Frequency')
            plt.title('Probability Distribution')
        
        plt.tight_layout()
        return self.fig_to_base64()
    
    def fig_to_base64(self):
        """Convert matplotlib figure to base64 string for HTML display"""
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        return image_base64

# Initialize analyzer
analyzer = RegressionAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files['file']
            regression_type = request.form.get('regression_type', 'linear')

            if file.filename == '':
                return render_template('upload.html', error='No file selected', regression_type=regression_type)

            # Save uploaded file to server uploads/ directory
            filename = secure_filename(file.filename)
            if filename == '':
                return render_template('upload.html', error='Invalid filename', regression_type=regression_type)

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # Read file based on saved extension
            if filename.endswith('.csv'):
                df = pd.read_csv(save_path)
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(save_path)
            else:
                return render_template('upload.html', error='Unsupported file format', regression_type=regression_type)

            # Get column information
            columns = df.columns.tolist()
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

            if not numeric_columns:
                return render_template('upload.html', error='No numeric columns found in the data', regression_type=regression_type)

            # Store small metadata in session (filename + columns) rather than full data
            session['uploaded_filename'] = filename
            session['regression_type'] = regression_type
            session['columns'] = columns
            session['numeric_columns'] = numeric_columns

            return render_template('upload.html', 
                                 columns=columns,
                                 numeric_columns=numeric_columns,
                                 regression_type=regression_type,
                                 df_preview=df.head(10).to_dict('records'),
                                 uploaded_filename=filename)
            
        except Exception as e:
            return render_template('upload.html', error=f'Error: {str(e)}', regression_type=request.form.get('regression_type', 'linear'))
    
    # GET request
    regression_type = request.args.get('regression_type', 'linear')
    return render_template('upload.html', regression_type=regression_type)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get form data
        regression_type = request.form.get('regression_type', 'linear')
        target_column = request.form.get('target_column')
        feature_columns = request.form.getlist('feature_columns')
        
        print(f"DEBUG: Regression Type: {regression_type}")
        print(f"DEBUG: Target Column: {target_column}")
        print(f"DEBUG: Feature Columns: {feature_columns}")
        
        if not target_column or not feature_columns:
            return render_template('upload.html', error='Please select both target and feature columns', regression_type=regression_type)
        
        # Load data from previously saved uploaded file (stored by /upload)
        uploaded_filename = request.form.get('uploaded_filename') or session.get('uploaded_filename')
        if not uploaded_filename:
            return render_template('upload.html', error='No uploaded file found. Please upload your file first.', regression_type=regression_type)

        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_filename))
        if not os.path.exists(saved_path):
            return render_template('upload.html', error='Uploaded file not found on server. Please re-upload.', regression_type=regression_type)

        # Read file from disk
        if saved_path.endswith('.csv'):
            df = pd.read_csv(saved_path)
        elif saved_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(saved_path)
        else:
            return render_template('upload.html', error='Unsupported file format', regression_type=regression_type)
        
        # Perform regression analysis
        if regression_type == 'linear':
            results = analyzer.perform_linear_regression(df, target_column, feature_columns)
        elif regression_type == 'polynomial':
            degree = int(request.form.get('degree', 2))
            results = analyzer.perform_polynomial_regression(df, target_column, feature_columns, degree)
        elif regression_type == 'logistic':
            results = analyzer.perform_logistic_regression(df, target_column, feature_columns)
        else:
            return render_template('upload.html', error=f'Invalid regression type: {regression_type}', regression_type=regression_type)
        
        # Add additional information to results
        results['regression_type'] = regression_type
        results['target_column'] = target_column
        results['feature_columns'] = feature_columns
        results['data_preview'] = df.head(5).to_dict('records')
        # Normalize coefficients and prepare table for template
        try:
            # For logistic, coefficients may be 2D (classes x features)
            if 'coefficients' in results:
                coeffs = results['coefficients']
                if isinstance(coeffs, list) and len(coeffs) > 0 and isinstance(coeffs[0], list):
                    # Flatten to first row for display
                    coeffs_display = coeffs[0]
                else:
                    coeffs_display = coeffs
                # ensure numeric
                coeffs_display = [float(c) for c in coeffs_display]
                results['coefficients_display'] = coeffs_display
                # pair features and coefficients (truncate/pad safely)
                paired = []
                for i, feat in enumerate(feature_columns):
                    coef_val = coeffs_display[i] if i < len(coeffs_display) else 0.0
                    paired.append((feat, coef_val))
                results['coef_table'] = paired
            else:
                results['coefficients_display'] = []
                results['coef_table'] = []

            # normalize intercept to float for template formatting
            if 'intercept' in results:
                try:
                    results['intercept'] = float(results['intercept'])
                except Exception:
                    # if intercept is list (logistic), take first element
                    if isinstance(results['intercept'], (list, tuple)) and len(results['intercept']) > 0:
                        results['intercept'] = float(results['intercept'][0])
                    else:
                        results['intercept'] = 0.0
        except Exception:
            # In case anything goes wrong preparing display values, fallback to safe defaults
            results.setdefault('coef_table', [])
            results.setdefault('intercept', 0.0)
        
        return render_template('results.html', results=results)
        
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return render_template('upload.html', error=f'Analysis error: {str(e)}', regression_type=request.form.get('regression_type', 'linear'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)