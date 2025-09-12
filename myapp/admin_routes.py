import json
import csv
from io import StringIO
from datetime import datetime, timedelta
from flask import render_template,request,redirect,flash,redirect,url_for,session,make_response
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required, logout_user,current_user, LoginManager,login_user,login_manager
from myapp import app,myforms,csrf,mail
from myapp.myforms import StatusUpdateForm
from myapp.models import User,Admin,UserRequest,ApprovalStatusEnum,db
from flask_mail import Message



def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache



@app.route('/admin/dashboard/')
@nocache
def admin_dashboard():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    pending_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.PENDING).count()
    approved_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.APPROVED).count()
    rejected_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.REJECTED).count()
    terminated_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.TERMINATED).count()
    admin_pending_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.PENDING).all()
    # Get the total number of requests
    total_requests = db.session.query(UserRequest).count()
    return render_template('admin/admin_dashboard.html', pending_requests=pending_requests,
                           approved_requests=approved_requests,rejected_requests=rejected_requests,
                           terminated_requests=terminated_requests, total_requests=total_requests, requests=admin_pending_requests)


@app.route('/admin/users/')
@nocache
def admin_users():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin/users.html',users=users)


@app.route('/admin/userdetails/<int:user_id>/')
@nocache
def admin_user_details(user_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    requests = UserRequest.query.filter_by(user_id=user_id).all()
    return render_template('admin/user_details.html', user=user, requests=requests)


@app.route('/admin/users/remove/<int:user_id>/', methods=['POST'])
@nocache
def admin_remove_user(user_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User removed successfully', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/toggle/<int:user_id>/', methods=['POST'])
@nocache
def admin_toggle_user(user_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    user.is_enabled = not user.is_enabled
    db.session.commit()
    status = 'enabled' if user.is_enabled else 'disabled'
    flash(f'User {user.user_fname} {user.user_lname} has been {status}', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/request/')
@nocache
def admin_requests():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    status_filter = request.args.get('status_filter') or ''
    start_date = request.args.get('start_date') or ''
    end_date = request.args.get('end_date') or ''
    search_query = request.args.get('search_query') or ''
    page = request.args.get('page', 1, type=int)
    query = UserRequest.query.options(db.joinedload(UserRequest.user)).join(User)
    if status_filter and status_filter != 'all' and status_filter in ApprovalStatusEnum.__members__:
        query = query.filter(UserRequest.status == ApprovalStatusEnum[status_filter])
    if search_query:
        query = query.filter(
            db.or_(
                UserRequest.fullname.ilike(f'%{search_query}%'),
                UserRequest.company.ilike(f'%{search_query}%'),
                UserRequest.job_role.ilike(f'%{search_query}%'),
                User.user_fname.ilike(f'%{search_query}%'),
                User.user_lname.ilike(f'%{search_query}%')
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
    requests = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/requests.html', requests=requests, status_filter=status_filter or 'all', start_date=start_date, end_date=end_date, search_query=search_query)


@app.route('/admin/request/export/')
@nocache
def admin_requests_export():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))

    status_filter = request.args.get('status_filter') or ''
    start_date = request.args.get('start_date') or ''
    end_date = request.args.get('end_date') or ''
    search_query = request.args.get('search_query') or ''

    query = UserRequest.query.options(db.joinedload(UserRequest.user)).join(User)
    if status_filter and status_filter != 'all' and status_filter in ApprovalStatusEnum.__members__:
        query = query.filter(UserRequest.status == ApprovalStatusEnum[status_filter])
    if search_query:
        query = query.filter(
            db.or_(
                UserRequest.fullname.ilike(f'%{search_query}%'),
                UserRequest.company.ilike(f'%{search_query}%'),
                UserRequest.job_role.ilike(f'%{search_query}%'),
                User.user_fname.ilike(f'%{search_query}%'),
                User.user_lname.ilike(f'%{search_query}%')
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
    # Write header
    cw.writerow(['Request No', 'Visitor\'s Name', 'Expected Date', 'Departure Date', 'Created Date', 'Requested By', 'Status'])
    for req in requests:
        cw.writerow([
            req.request_no,
            req.fullname,
            req.expected_date,
            req.departure_date,
            req.created_date,
            f"{req.user.user_fname} {req.user.user_lname}" if req.user else '',
            req.status.value if req.status else ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=requests_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/admin/requestdetails/<int:request_id>/',methods=['GET','POST'])
@nocache
def admin_request_details(request_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    req = UserRequest.query.get_or_404(request_id)
    users = User.query.all()
    form = StatusUpdateForm()
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status and new_status in ApprovalStatusEnum.__members__:
            req.status = ApprovalStatusEnum[new_status]
            db.session.commit()

            # Send email notification to user on approval
            if new_status == 'APPROVED':
                email = req.user.user_email
                name = req.user.user_fname
                msg = Message("Access Request Approved",
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[email])
                msg.body = f"Dear {name},\n\nYour access request has been approved by the Access Controller.\n\nBest regards,\nLadol Security Team"
                try:
                    mail.send(msg)
                except Exception as e:
                    app.logger.error(f"Failed to send approval email: {e}")
                    flash('Access request approved but failed to send email notification.', 'warning')
                else:
                    flash('Access request approved', 'success')
            elif new_status == 'REJECTED':
                email = req.user.user_email
                name = req.user.user_fname
                msg = Message("Access Request Rejected",
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[email])
                msg.body = f"Dear {name},\n\nYour access request has been rejected by the Access Controller.\n\nBest regards,\nLadol Security Team"
                try:
                    mail.send(msg)
                except Exception as e:
                    app.logger.error(f"Failed to send rejection email: {e}")
                    flash('Access request rejected but failed to send email notification.', 'warning')
                else:
                    flash('Access request rejected', 'danger')
            elif new_status == 'TERMINATED':
                email = req.user.user_email
                name = req.user.user_fname
                msg = Message("Access Request Terminated",
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[email])
                msg.body = f"Dear {name},\n\nYour access request has been terminated by the Access Controller.\n\nBest regards,\nLadol Security Team"
                try:
                    mail.send(msg)
                except Exception as e:
                    app.logger.error(f"Failed to send termination email: {e}")
                    flash('Access request terminated but failed to send email notification.', 'warning')
                else:
                    flash('Access request terminated', 'info')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid status update', 'danger')
    documents = json.loads(req.document) if req.document else []
    return render_template('admin/request_details.html',request=req, form=form, documents=documents, users=users)

        

        

@app.route('/admin/login/',methods=['GET','POST'])
def admin_login():
    loginform = myforms.LoginForm()
    if request.method == 'GET':
        return render_template('admin/login.html',loginform=loginform)
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Email and password are required', category='danger')
            return redirect('/admin/login/')
        check = Admin.query.filter(Admin.admin_username==email).first()
        if check:
            stored_pass = check.admin_password
            chk = check_password_hash(stored_pass, password)
            if chk:
                login_user(check)
                session['adminuseronline'] = check.admin_id
                return redirect('/admin/dashboard/')
            else:
                flash('Invalid username or password',category='danger')
                return redirect('/admin/login/')
        else:
            flash('Invalid username',category='danger')
            return redirect('/admin/login/')
        

@app.route('/admin/logout/')
@nocache
def admin_logout():
    logout_user()
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin/change_password/', methods=['GET', 'POST'])
@nocache
def admin_change_password():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    if request.method == 'GET':
        return render_template('admin/change_password.html')
    else:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        admin_id = session['adminuseronline']
        admin = Admin.query.get(admin_id)
        if admin is None:
            flash('Admin user not found', 'danger')
            return redirect(url_for('admin_login'))
        if not current_password or not new_password or not confirm_password:
            flash('All password fields are required', 'danger')
            return redirect(url_for('admin_change_password'))
        if not check_password_hash(admin.admin_password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('admin_change_password'))
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('admin_change_password'))
        admin.admin_password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect(url_for('admin_dashboard'))


        