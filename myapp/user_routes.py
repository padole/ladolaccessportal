import os
import json
import csv
from io import StringIO
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from functools import wraps
from flask import render_template,request,redirect,flash,redirect,url_for,session,make_response
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import current_user,login_required,login_user,logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from wtforms.validators import DataRequired
# from flask_login import login_required,current_user
from myapp import app,myforms,csrf,mail
from myapp.models import User,UserRequest,ApprovalStatusEnum,db



s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache



@app.route('/')
def home():
    userid = session.get("useronline")
    if userid:
        deets = User.query.get(userid)
    else:
        deets = None

    return render_template('user/index.html',deets=deets)



@app.route('/login/',methods=['GET','POST'])
@nocache
def login():
    loginform = myforms.LoginForm()
    if request.method == 'GET':
        return render_template('user/login.html',loginform=loginform)
    else:
        if loginform.validate_on_submit():
            email = loginform.email.data
            password = loginform.password.data
            deets = db.session.query(User).filter(User.user_email==email).first()
            if deets and email and deets.check_password(password):
                if not deets.is_enabled:
                    flash('Your account has been disabled. Please contact the administrator.', category='danger')
                    return redirect(url_for('login'))
                login_user(deets)
                session['useronline'] = deets.user_id
                flash('Login Successful',category='success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password',category='danger')
                return redirect(url_for('login'))
                # return render_template('user/login.html',loginform=loginform)
        else:
            flash('Invalid email',category='danger')
            return redirect(url_for('login'))
        # return render_template('user/login.html',loginform=loginform)



@app.route("/get-started/")
def get_started():
    if session.get('useronline'):  # if user is logged in
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))
 

@app.route('/register/',methods=['GET','POST'])
def register():
    form = myforms.RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data

        try:
            # Check if email already exists
            if User.query.filter_by(user_email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))

            # Create new user
            user = User(user_fname=fname, user_lname=lname, user_email=email, user_phone=phone)
            user.set_password(password)

            # Add to database
            db.session.add(user)
            db.session.commit()

            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('user/register.html', form=form)
    





@app.route('/user/new_request/', methods=['GET', 'POST'])
@nocache
def new_request():
    form = myforms.NewRequest()
    userid = session.get("useronline")
    if not userid:
        flash('You must be logged in to make a request', 'danger')
        return redirect(url_for('login'))
    deets = User.query.get(userid) 

    if request.method == 'POST' and form.validate_on_submit():
        filenames = []
        try:
            if form.document.data:
                for file in form.document.data:
                    if file:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        filenames.append(filename)

            # Generate next request number
            max_id = db.session.query(db.func.max(UserRequest.request_id)).scalar() or 0
            request_no = f"LFZ-{str(max_id + 1).zfill(3)}"

            new_request = UserRequest(
                request_no=request_no,
                fullname=form.fullname.data,
                company=form.company.data,
                job_role=form.job_role.data,
                email_address=form.email.data,
                phone_number=form.phone.data,
                id_card=form.id_card.data,
                expected_date=form.expected_date.data,
                departure_date=form.departure_date.data,
                duration=form.duration.data,
                location=form.location.data,
                purpose=form.purpose.data,
                user_id=userid,
                document=json.dumps(filenames) if filenames else None
            )
            db.session.add(new_request)
            db.session.commit()

            # Send email notification to user
            try:
                msg = Message("Access Request Created",
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[deets.user_email])
                msg.body = f"Dear {deets.user_fname},\n\nYour access request has been successfully created.\n\nRequest Details:\n- Visitor's Name: {form.fullname.data}\n- Company: {form.company.data}\n- Location: {form.location.data}\n- Purpose of Visit: {form.purpose.data}\n\nYou will be notified once your request is reviewed by the Access Controller.\n\nBest regards,\nLadol Security Team"
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Failed to send user email notification: {e}")

            # Send email notification to admin
            try:
                admin_msg = Message("New Access Request Created",
                                    sender=app.config['MAIL_DEFAULT_SENDER'],
                                    recipients=[app.config['MAIL_ADMIN']])
                admin_msg.body = f"Dear Admin,\n\nA new access request has been created.\n\nRequest Details:\n- Visitor's Name: {form.fullname.data}\n- Company: {form.company.data}\n- Location: {form.location.data}\n- Purpose of Visit: {form.purpose.data}\n- Requested by: {deets.user_fname} {deets.user_lname} ({deets.user_email})\n\nPlease review the request in the admin dashboard.\n\nBest regards,\nLadol Security Team"
                mail.send(admin_msg)
            except Exception as e:
                app.logger.error(f"Failed to send admin email notification: {e}")

            flash('Request created successfully', 'success')
            return redirect(url_for('user_request'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating new request: {e}")
            flash('An error occurred while creating the request. Please try again.', 'danger')
            return redirect(url_for('new_request'))
    users = User.query.all()
    return render_template('user/new_request.html', form=form, users=users, deets=deets)
        



# 

@app.route('/user/dashboad/')
@nocache
# @login_required
def dashboard():
    userid = session.get("useronline")
    if not userid:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    # Count the number of requests for each status
    pending_requests = db.session.query(UserRequest).filter(UserRequest.user_id==userid, UserRequest.status == ApprovalStatusEnum.PENDING).count()
    approved_requests = db.session.query(UserRequest).filter(UserRequest.user_id==userid, UserRequest.status == ApprovalStatusEnum.APPROVED).count()
    rejected_requests = db.session.query(UserRequest).filter(UserRequest.user_id==userid, UserRequest.status == ApprovalStatusEnum.REJECTED).count()
    terminated_requests = db.session.query(UserRequest).filter(UserRequest.user_id==userid, UserRequest.status == ApprovalStatusEnum.TERMINATED).count()
    # Get the total number of requests
    total_requests = db.session.query(UserRequest).filter(UserRequest.user_id == userid).count()
    # Get the list of pending requests
    pending_requests_list = db.session.query(UserRequest).filter(UserRequest.user_id==userid, UserRequest.status == ApprovalStatusEnum.PENDING).all()
    deets = User.query.get(userid)
    return render_template('user/user_dashboard.html', pending_requests=pending_requests, approved_requests=approved_requests,
                           rejected_requests=rejected_requests, terminated_requests=terminated_requests,total_requests=total_requests, pending_requests_list=pending_requests_list, deets=deets)

    

@app.route('/user/request/')
@nocache
def user_request():
    userid = session.get("useronline")
    if not userid:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

    status_filter = request.args.get('status_filter') or ''
    start_date = request.args.get('start_date') or ''
    end_date = request.args.get('end_date') or ''
    search_query = request.args.get('search_query') or ''
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = UserRequest.query.filter_by(user_id=userid)
    if status_filter and status_filter != 'all' and status_filter in ApprovalStatusEnum.__members__:
        query = query.filter(UserRequest.status == ApprovalStatusEnum[status_filter])
    if search_query:
        query = query.filter(
            db.or_(
                UserRequest.fullname.ilike(f'%{search_query}%'),
                UserRequest.company.ilike(f'%{search_query}%'),
                UserRequest.job_role.ilike(f'%{search_query}%')
            )
        )
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(UserRequest.created_date >= start_date_obj)
        except ValueError:
            pass
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(UserRequest.created_date < end_date_obj)
        except ValueError:
            pass

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    deets = User.query.get(userid)
    return render_template('user/user_requests.html', deets=deets, requests=pagination, status_filter=status_filter or 'all', start_date=start_date, end_date=end_date, search_query=search_query)


@app.route('/user/request/export/')
@nocache
def user_requests_export():
    userid = session.get("useronline")
    if not userid:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

    status_filter = request.args.get('status_filter') or ''
    start_date = request.args.get('start_date') or ''
    end_date = request.args.get('end_date') or ''
    search_query = request.args.get('search_query') or ''

    query = UserRequest.query.filter_by(user_id=userid)
    if status_filter and status_filter != 'all' and status_filter in ApprovalStatusEnum.__members__:
        query = query.filter(UserRequest.status == ApprovalStatusEnum[status_filter])
    if search_query:
        query = query.filter(
            db.or_(
                UserRequest.fullname.ilike(f'%{search_query}%'),
                UserRequest.company.ilike(f'%{search_query}%'),
                UserRequest.job_role.ilike(f'%{search_query}%')
            )
        )
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(UserRequest.created_date >= start_date_obj)
        except ValueError:
            pass
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(UserRequest.created_date < end_date_obj)
        except ValueError:
            pass

    requests = query.all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Request No', 'Visitor\'s Name', 'Job Role', 'Expected Date', 'Departure Date', 'Created Date', 'Status'])
    for req in requests:
        cw.writerow([
            req.request_no,
            req.fullname,
            req.job_role,
            req.expected_date,
            req.departure_date,
            req.created_date,
            req.status.value if req.status else ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=user_requests_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/logout/')
@nocache
def logout():
    logout_user()
    if session.get('useronline') != None:
        session.pop('useronline', None)
    return redirect(url_for('home'))




@app.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(user_email=email).first()
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)

            # Send email
            msg = Message("Password Reset Request",
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash("A password reset link has been sent to your email.", "success")
            return redirect(url_for('login'))
        else:
            flash("Email not found.", "danger")
    return render_template('user/forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)  # 1hr expiry
    except Exception:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password', token=token))
        user = User.query.filter_by(user_email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash("Your password has been reset. Please log in.", "success")
            return redirect(url_for('login'))
    return render_template('user/reset_password.html', token=token)



@app.route("/change_password/", methods=["GET", "POST"])
@nocache
def change_password():
    userid = session.get("useronline")
    if not userid:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    user = User.query.get(userid)

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check current password
        if not user.check_password(current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for("change_password"))

        # Check match
        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("change_password"))

        # Update password using the set_password method
        user.set_password(new_password)
        db.session.commit()

        flash("Password changed successfully!", "success")
        return redirect(url_for("login"))  # redirect anywhere you like

    return render_template("user/change_password.html")

