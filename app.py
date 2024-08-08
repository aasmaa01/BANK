
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from sqlalchemy.exc import IntegrityError
import logging
from logging.handlers import RotatingFileHandler
from flask_login import LoginManager, login_required, UserMixin
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from celery import Celery
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

# Create SQLAlchemy, Migrate, Bcrypt, CSRFProtect, Cache, and Celery instances
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'simple'})
celery = Celery()

class LoginForm(FlaskForm):
    email_address = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Set the login view

    # Initialize bcrypt
    bcrypt.init_app(app)

    # Initialize CSRF protection
    csrf.init_app(app)

    # Initialize cache
    cache.init_app(app)

    # Initialize Celery
    celery.conf.update(app.config)
    celery.conf.update(
        result_backend=Config.CELERY_RESULT_BACKEND,
        broker_url=Config.CELERY_BROKER_URL
    )

    # Setup logging
    if not app.debug:
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


    # Import models after initializing db and migrate
    from models.User import User
    from models.Account import Account
    from models.Transaction import Transaction
    from models.Agency import Agency
    from models.ContactMessage import ContactMessage
    from models.Loan import Loan
    from models.Repayment import Repayment
    from models.Customer import Customer
    from models.Card import Card
    from models.Credit import Credit

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.error(f"Page not found: {error}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal server error: {error}")
        return render_template('500.html'), 500

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email_address')
        password = data.get('password')
    
        user = User.query.filter_by(email_address=email).first()

        if user and user.check_password(password):  # Ensure User model has a method to check password
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/main-dashboard')
    def main_dashboard():
        return render_template('dashboard.html')

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        
    
        try:
            # Ensure all required fields are present
            required_fields = ['email_address', 'password', 'date_of_birth']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
        
            # Hash the password before storing
            hashed_password = generate_password_hash(data['password'])
        
            new_user = User(
                id=data.get('id'),
                username=data.get('username'),
                password_hash=hashed_password,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                date_of_birth=data.get('date_of_birth'),
                address=data.get('address'),
                phone_number=data.get('phone_number'),
                email_address=data.get('email_address'),
                nin_cust=data.get('nin_cust'),
                rib_cust=data.get('rib_cust'),
                agency_id=data.get('agency_id'),
                registration_date=data.get('registration_date')
            )

        
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User created successfully!"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "User with this email already exists!"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/account', methods=['POST'])
    def create_account():
        data = request.get_json()
        try:
            required_fields = ['customer_id', 'account_number', 'account_type', 'balance', 'agency_id', 'user_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            new_account = Account(
                customer_id=data['customer_id'],
                account_number=data['account_number'],
                account_type=data['account_type'],
                balance=data['balance'],
                agency_id=data['agency_id'],
                user_id=data['user_id']
            )
            db.session.add(new_account)
            db.session.commit()
            return jsonify({"message": "Account created successfully!"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Account with this number already exists!"}), 400
        except Exception as e:
            app.logger.error(f"Error creating account: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop('user_id', None)
        return jsonify({"message": "Logged out successfully"}), 200

    @app.route('/customer/<int:customer_id>', methods=['GET'])
    def get_customer_info(customer_id):
        customer = User.query.get(customer_id)
        if customer:
            return jsonify(customer.to_dict())
        else:
            return jsonify({"error": "Customer not found"}), 404

    @app.route('/account/<int:account_id>', methods=['GET'])
    def get_account_details(account_id):
        account = Account.query.get(account_id)
        if account:
            return jsonify(account.to_dict())
        else:
            return jsonify({"error": "Account not found"}), 404

    @app.route('/agency/<int:agency_id>', methods=['GET'])
    def get_agency_details(agency_id):
        agency = Agency.query.get(agency_id)
        if agency:
            return jsonify(agency.to_dict())
        else:
            return jsonify({"error": "Agency not found"}), 404

    @app.route('/transaction', methods=['POST'])
    def create_transaction():
        data = request.get_json()
        try:
            new_transaction = Transaction(
                amount=data['amount'],
                currency=data['currency'],
                date=data['date'],
                transaction_type=data['transaction_type']
            )
            db.session.add(new_transaction)
            db.session.commit()
            return jsonify({"message": "Transaction created successfully"}), 201
        except Exception as e:
            app.logger.error(f"Error creating transaction: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/transfer', methods=['POST'])
    def transfer():
        data = request.get_json()
        try:
            sender_account = Account.query.get(data['from_account_id'])
            receiver_account = Account.query.get(data['to_account_id'])

            if sender_account and receiver_account:
                if sender_account.balance >= data['amount']:
                    sender_account.balance -= data['amount']
                    receiver_account.balance += data['amount']

                    transaction_sender = Transaction(
                        amount=data['amount'],
                        currency=data['currency'],
                        date=data['date'],
                        transaction_type='debit'
                    )
                    transaction_receiver = Transaction(
                        amount=data['amount'],
                        currency=data['currency'],
                        date=data['date'],
                        transaction_type='credit'
                    )
                    db.session.add(transaction_sender)
                    db.session.add(transaction_receiver)
                    db.session.commit()

                    return jsonify({"message": "Transfer successful"}), 200
                else:
                    return jsonify({"error": "Insufficient funds"}), 400
            else:
                return jsonify({"error": "Invalid accounts"}), 404
        except Exception as e:
            app.logger.error(f"Error during transfer: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/cards', methods=['POST'])
    def add_card():
        data = request.get_json()
        try:
            new_card = Card(
                card_number=data['card_number'],
                card_type=data['card_type'],
                expiration_date=data['expiration_date'],
                cardholder_name=data['cardholder_name'],
                balance=data['balance'],
                customer_id=data['customer_id']
            )
            db.session.add(new_card)
            db.session.commit()
            return jsonify({'message': 'Card added successfully!'}), 201
        except Exception as e:
            app.logger.error(f"Error adding card: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/credits', methods=['POST'])
    def add_credit():
        data = request.get_json()
        try:
            new_credit = Credit(
                card_id=data['card_id'],
                credit_amount=data['credit_amount'],
                credit_date=data['credit_date']
            )
            card = Card.query.get(data['card_id'])
            if card:
                card.balance += data['credit_amount']
                db.session.add(new_credit)
                db.session.commit()
                return jsonify({'message': 'Credit added successfully!'}), 201
            return jsonify({'error': 'Card not found!'}), 404
        except Exception as e:
            app.logger.error(f"Error adding credit: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/loan/<int:loan_id>', methods=['GET'])
    def get_loan_details(loan_id):
        loan = Loan.query.get(loan_id)
        if loan:
            return jsonify(loan.to_dict())
        else:
            return jsonify({"error": "Loan not found"}), 404

    @app.route('/repayment/<int:repayment_id>', methods=['GET'])
    def get_repayment_details(repayment_id):
        repayment = Repayment.query.get(repayment_id)
        if repayment:
            return jsonify(repayment.to_dict())
        else:
            return jsonify({"error": "Repayment not found"}), 404

    @app.route('/loan', methods=['POST'])
    def create_loan():
        data = request.get_json()
        try:
            required_fields = ['client_id', 'loan_amount', 'interest_rate', 'start_date', 'end_date']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            new_loan = Loan(
                client_id=data['client_id'],
                loan_amount=data['loan_amount'],
                interest_rate=data['interest_rate'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                outstanding_balance=data.get('outstanding_balance', 0)
            )
            db.session.add(new_loan)
            db.session.commit()
            return jsonify({"message": "Loan created successfully!"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Error creating loan"}), 400
        except Exception as e:
            app.logger.error(f"Error creating loan: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/repayment', methods=['POST'])
    def create_repayment():
        data = request.get_json()
        try:
            required_fields = ['loan_id', 'repayment_date', 'repayment_amount']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            new_repayment = Repayment(
                loan_id=data['loan_id'],
                repayment_date=data['repayment_date'],
                repayment_amount=data['repayment_amount']
            )
            db.session.add(new_repayment)
            db.session.commit()
            return jsonify({"message": "Repayment created successfully!"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Error creating repayment"}), 400
        except Exception as e:
            app.logger.error(f"Error creating repayment: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/contact', methods=['POST'])
    def contact():
        data = request.get_json()
        if all(key in data for key in ('full_name', 'email_address', 'phone_number', 'message')):
            contact_message = ContactMessage(
                full_name=data['full_name'],
                email_address=data['email_address'],
                phone_number=data['phone_number'],
                message=data['message']
            )
            db.session.add(contact_message)
            db.session.commit()
            return jsonify({"message": "Message received"}), 201
        else:
            return jsonify({"error": "Missing data"}), 400

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)