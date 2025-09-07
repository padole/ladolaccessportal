import json
from flask import render_template,request,redirect,flash,redirect,url_for,session,make_response
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required, logout_user,current_user, LoginManager,login_user,login_manager
from myapp import app,myforms,csrf
from myapp.myforms import StatusUpdateForm
from myapp.models import User,Admin,UserRequest,ApprovalStatusEnum,db




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
    admin_pending_requests = db.session.query(UserRequest).filter(UserRequest.status == ApprovalStatusEnum.PENDING).all()
    # Get the total number of requests
    total_requests = db.session.query(UserRequest).count()
    return render_template('admin/admin_dashboard.html', pending_requests=pending_requests,
                           approved_requests=approved_requests,rejected_requests=rejected_requests,
                           total_requests=total_requests, requests=admin_pending_requests)


@app.route('/admin/users/')
@nocache
def admin_users():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin/users.html',users=users)


@app.route('/admin/users/remove/<int:user_id>', methods=['POST'])
@nocache
def admin_remove_user(user_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User removed successfully', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/request/')
@nocache
def admin_requests():
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    status_filter = request.args.get('status_filter') or ''
    date_filter = request.args.get('date_filter') or ''
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
    # if date_filter:
    #     try:
    #         filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    #         query = query.filter(UserRequest.expected_date == filter_date)
    #     except ValueError:
    #         pass  # Invalid date, ignore
    requests = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/requests.html', requests=requests, status_filter=status_filter or 'all', date_filter=date_filter or '', search_query=search_query)


@app.route('/admin/requestdetails/<int:request_id>/',methods=['GET','POST'])
@nocache
def admin_request_details(request_id):
    if not session.get('adminuseronline'):
        return redirect(url_for('admin_login'))
    req = UserRequest.query.get_or_404(request_id)
    form = StatusUpdateForm()
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status and new_status in ApprovalStatusEnum.__members__:
            req.status = ApprovalStatusEnum[new_status]
            db.session.commit()
            if new_status == 'APPROVED':
                flash('Access request approved', 'success')
            elif new_status == 'REJECTED':
                flash('Access request rejected', 'danger')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid status update', 'danger')
    documents = json.loads(req.document) if req.document else []
    return render_template('admin/request_details.html',request=req, form=form, documents=documents)

        

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


        