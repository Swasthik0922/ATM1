from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# In-memory database for demonstration purposes
users = {
    '123456789': {
        'pin': '1234',
        'name': 'John Doe',
        'balance': 5000.00,
        'transactions': []
    },
    '987654321': {
        'pin': '4321',
        'name': 'Jane Smith',
        'balance': 3500.00,
        'transactions': []
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_number = request.form['account_number']
        pin = request.form['pin']
        
        if account_number in users and users[account_number]['pin'] == pin:
            session['logged_in'] = True
            session['account_number'] = account_number
            flash(f'Welcome {users[account_number]["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid account number or PIN', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        account_number = session['account_number']
        user_data = users[account_number]
        return render_template('dashboard.html', user=user_data)
    return redirect(url_for('login'))

@app.route('/check_balance')
def check_balance():
    if 'logged_in' in session and session['logged_in']:
        account_number = session['account_number']
        balance = users[account_number]['balance']
        
        # Log this transaction
        transaction = {
            'type': 'Balance Inquiry',
            'amount': 0,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'balance_after': balance
        }
        users[account_number]['transactions'].append(transaction)
        
        return render_template('balance.html', balance=balance)
    return redirect(url_for('login'))

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    account_number = session['account_number']
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Please enter a positive amount', 'error')
            elif amount > users[account_number]['balance']:
                flash('Insufficient funds', 'error')
            else:
                users[account_number]['balance'] -= amount
                
                # Log this transaction
                transaction = {
                    'type': 'Withdrawal',
                    'amount': amount,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': users[account_number]['balance']
                }
                users[account_number]['transactions'].append(transaction)
                
                flash(f'Successfully withdrew ${amount:.2f}', 'success')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash('Please enter a valid amount', 'error')
    
    return render_template('withdraw.html', balance=users[account_number]['balance'])

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    account_number = session['account_number']
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Please enter a positive amount', 'error')
            else:
                users[account_number]['balance'] += amount
                
                # Log this transaction
                transaction = {
                    'type': 'Deposit',
                    'amount': amount,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': users[account_number]['balance']
                }
                users[account_number]['transactions'].append(transaction)
                
                flash(f'Successfully deposited ${amount:.2f}', 'success')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash('Please enter a valid amount', 'error')
    
    return render_template('deposit.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    account_number = session['account_number']
    
    if request.method == 'POST':
        recipient = request.form['recipient_account']
        
        try:
            amount = float(request.form['amount'])
            
            if recipient not in users:
                flash('Recipient account not found', 'error')
            elif amount <= 0:
                flash('Please enter a positive amount', 'error')
            elif amount > users[account_number]['balance']:
                flash('Insufficient funds', 'error')
            else:
                users[account_number]['balance'] -= amount
                users[recipient]['balance'] += amount
                
                # Log this transaction for sender
                transaction = {
                    'type': f'Transfer to {recipient}',
                    'amount': amount,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': users[account_number]['balance']
                }
                users[account_number]['transactions'].append(transaction)
                
                # Log this transaction for recipient
                transaction = {
                    'type': f'Transfer from {account_number}',
                    'amount': amount,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'balance_after': users[recipient]['balance']
                }
                users[recipient]['transactions'].append(transaction)
                
                flash(f'Successfully transferred ${amount:.2f} to account {recipient}', 'success')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash('Please enter a valid amount', 'error')
    
    return render_template('transfer.html', balance=users[account_number]['balance'])

@app.route('/transactions')
def transactions():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    account_number = session['account_number']
    user_transactions = users[account_number]['transactions']
    
    return render_template('transactions.html', transactions=user_transactions)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)