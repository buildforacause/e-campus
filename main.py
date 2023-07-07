from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from forms import CreateEventForm, RegisterForm, LoginForm, CommentForm, LostFoundForm, GrievanceForm, AttendanceForm, \
    StackQuesForm, CommentFormStack, CommentFormProject, ProjectPostForm, MarksForm
from flask_gravatar import Gravatar
import smtplib
import plotly
import json
import plotly.express as px
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_email = "ecampusnotifier@yahoo.com"
password = "olapykzlqtdsgbxk"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecampus2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONFIGURE TABLES


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    type = db.Column(db.String(20), default="student")
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    lostfoundcomments = relationship("LostFoundComment", back_populates="comment_author")
    lostfound = relationship("LostFound", back_populates="author")
    order = relationship("Order", back_populates="author")
    attendance = relationship("Attendance", back_populates="student")
    stackcomments = relationship("StackComment", back_populates="stack_comment_author")
    stackposts = relationship("StackPost", back_populates="stack_author")
    projectposts = relationship("ProjectPost", back_populates="project_author")
    projectcomments = relationship("ProjectComment", back_populates="project_comment_author")
    marks = relationship("Marks", back_populates="student")


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    total_days = db.Column(db.Integer, default=1)
    present_days = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    student = relationship("User", back_populates="attendance")
    date = db.Column(db.Date)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    comment = db.Column(db.Text, nullable=False)
    comment_author = relationship("User", back_populates="comments")
    parent_post = relationship("BlogPost", back_populates="comments")


class LostFoundComment(db.Model):
    __tablename__ = "lostfoundcomments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("lostfound.id"))
    comment = db.Column(db.Text, nullable=False)
    comment_author = relationship("User", back_populates="lostfoundcomments")
    parent_post = relationship("LostFound", back_populates="comments")


class LostFound(db.Model):
    __tablename__ = "lostfound"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(100), nullable=False)
    user_choice = db.Column(db.Text, nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    image = db.Column(db.String)
    author = relationship("User", back_populates="lostfound")
    comments = relationship("LostFoundComment", back_populates="parent_post")


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    order_desc = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="order")


class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(250), nullable=False, unique=True)
    item_price = db.Column(db.Float, nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)


class StackPost(db.Model):
    __tablename__ = "stackpost"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    question = db.Column(db.Text, nullable=False)
    user_choice = db.Column(db.Text, nullable=False)
    stack_author = relationship("User", back_populates="stackposts")
    stackcomments = relationship("StackComment", back_populates="stack_parent_post")


class StackComment(db.Model):
    __tablename__ = "stackcomments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("stackpost.id"))
    comment = db.Column(db.Text, nullable=False)
    stack_comment_author = relationship("User", back_populates="stackcomments")
    stack_parent_post = relationship("StackPost", back_populates="stackcomments")


class ProjectPost(db.Model):
    __tablename__ = "projectpost"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    user_choice = db.Column(db.Text, nullable=False)
    project_author = relationship("User", back_populates="projectposts")
    projectcomments = relationship("ProjectComment", back_populates="project_parent_post")


class ProjectComment(db.Model):
    __tablename__ = "projectcomments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("projectpost.id"))
    comment = db.Column(db.Text, nullable=False)
    project_comment_author = relationship("User", back_populates="projectcomments")
    project_parent_post = relationship("ProjectPost", back_populates="projectcomments")


class Marks(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    cgpa = db.Column(db.Float)
    sem = db.Column(db.String(5))
    student = relationship("User", back_populates="marks")


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash("You've already signed up with that email, log in instead!", "error")
            return redirect(url_for('login'))
        hashed_salted_psw = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=email,
            password=hashed_salted_psw,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", "error")
            return redirect(url_for('register', form=form))
        elif user and not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'error')
            return redirect(url_for('login', form=form))
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            comment = form.comment.data
            new_comment = Comment(
                comment=comment,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
        return render_template("post.html", post=requested_post, form=form)
    return render_template("post.html", post=requested_post, form=form)


@login_required
@app.route("/grievance", methods=["GET", "POST"])
def contact():
    if current_user.is_authenticated:
        form = GrievanceForm()
        if form.validate_on_submit():
            user_choice = form.user_choice.data
            email = form.email.data
            phone_no = form.phone_no.data
            grievance = form.grievance.data
            if user_choice == "Cleanliness":
                reciever = "aniruddha.fale@gmail.com"
            else:
                reciever = "sidsinghcs@gmail.com"
            with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                connection.starttls()
                connection.ehlo()
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=reciever,
                    msg=f"Subject:{user_choice} Issue\n\nMy name is {current_user.name} and my issue is {grievance}\nYou can contact me"
                        f" through the below given details:\nPhone No- {phone_no}\nEmail- {email}"
                )
            flash("Response has been submitted successfully!", "success")
    else:
        flash("You need to login first!")
        return redirect("/login")
    return render_template("contact.html", form=form)


@login_required
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreateEventForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@login_required
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreateEventForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@login_required
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@login_required
@app.route("/marks", methods=["GET", "POST"])
def upload_marks():
    form = MarksForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            f = request.files["file"]
            marks = pd.read_excel(f)
            for index, row in marks.iterrows():
                obj = Marks.query.filter_by(sem=row["sem"], student_id=row["studentid"]).first()
                if obj:
                    obj.cgpa = row["cgpa"]
                else:
                    try:
                        new_marks = Marks(
                            student_id=row["studentid"],
                            sem=row["sem"],
                            cgpa=row["cgpa"]
                        )
                        db.session.add(new_marks)
                        db.session.commit()
                    except:
                        flash("something went wrong", "error")
                        return render_template("marks.html", form=form)
            flash("Marks submitted successfully", "success")
        return render_template("marks.html", form=form)
    return render_template("marks.html", form=form)


# @login_required
# @app.route("/attendance", methods=["GET", "POST"])
# def attendance():
#     attendanceform = AttendanceForm()
#     if attendanceform.validate_on_submit():
#         f = request.files["attendancesheet"]
#         attendance_df = pd.read_excel(f)
#         for index, row in attendance_df.iterrows():
#             date_query = Attendance.query.filter_by(date=attendanceform.attendancedate.data).first()
#             if date_query:
#                 flash("Already Submitted for this day", "error")
#             else:
#                 try:
#                     total_query = Attendance.query.get(student_id=row["studentid"])
#                     total_query.total_days += 1
#                     if row['attendance'].lower() == "p":
#                         total_query.present_days += 1
#                 except:
#                     new_attendance = Attendance(
#                         student_id=row["studentid"],
#                         total_days=1,
#                         present_days=1,
#                         date=date.today()
#                     )
#                     db.session.add(new_attendance)
#                 finally:
#                     db.session.commit()
#         return redirect(url_for("attendance"))
#     return render_template("attendance.html", form=attendanceform)


@login_required
@app.route("/dashboard")
def dashboard():
    marks_obj = Marks.query.filter_by(student_id=current_user.id).values('sem', 'cgpa')
    marks_df = pd.DataFrame(list(marks_obj))
    fig = px.bar(marks_df, x=marks_df['sem'], y=marks_df['cgpa'], title=f"{current_user.name}'s Marks Plot")
    graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    avg = marks_df["cgpa"].mean()
    max_sem = marks_df.loc[marks_df["cgpa"] == marks_df["cgpa"].max()]["sem"].values[0][0]
    try:
        pred = prediction(marks_df.sort_values(by="sem", ascending=False)["cgpa"].values[0])
    except:
        pred = 0
    if pred >= 10:
        pred = 10
    elif pred <= 0:
        pred = 0
    return render_template("dashboard.html", graph=graph, avg=avg, max_sem=max_sem, df=list(marks_df.values.tolist()),
                           zip=zip, column_names=marks_df.columns, predicted_score=pred)


def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y * x) - n * m_y * m_x
    SS_xx = np.sum(x * x) - n * m_x * m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1 * m_x

    return b_0, b_1


def prediction(X):
    # observations / data
    x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    y = np.array([1, 2.5, 2.9, 4, 5.2, 6.1, 7, 8, 8.5, 10, 10])
    # estimating coefficients
    b = estimate_coef(x, y)
    y_pred = b[0] + b[1] * X
    return y_pred


@login_required
@app.route("/canteen_admin/<int:order_id>")
def delete_order(order_id):
    order_to_delete = Order.query.get(order_id)
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        message = """\
        <html>
        	<head>
        		<meta charset="utf-8" />
        		<title></title>
        		<style>
        			.invoice-box {
        				max-width: 800px;
        				margin: auto;
        				padding: 30px;
        				border: 1px solid #eee;
        				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
        				font-size: 16px;
        				line-height: 24px;
        				font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        				color: #555;
        			}
        			.invoice-box table {
        				width: 100%;
        				line-height: inherit;
        				text-align: left;
        			}
        			.invoice-box table td {
        				padding: 5px;
        				vertical-align: top;
        			}
        			.invoice-box table tr td:nth-child(2) {
        				text-align: right;
        			}
        			.invoice-box table tr.top table td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.top table td.title {
        				font-size: 45px;
        				line-height: 45px;
        				color: #333;
        			}
        			.invoice-box table tr.information table td {
        				padding-bottom: 40px;
        			}
                  .idno{
                  	font-weight: bold;
                    font-size: 60px;
                    padding-top:70px;
                    text-align: center;
                  }
                  .invoiceid{
                  	text-align: center;
                  }
        			.invoice-box table tr.heading td {
        				background: #eee;
        				border-bottom: 1px solid #ddd;
        				font-weight: bold;
        			}
        			.invoice-box table tr.details td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.item td {
        				border-bottom: 1px solid #eee;
        			}
        			.invoice-box table tr.item.last td {
        				border-bottom: none;
        			}
        			.invoice-box table tr.total td:nth-child(2) {
        				border-top: 2px solid #eee;
        				font-weight: bold;
        			}
        			@media only screen and (max-width: 600px) {
        				.invoice-box table tr.top table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        				.invoice-box table tr.information table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        			}
        			/** RTL **/
        			.invoice-box.rtl {
        				direction: rtl;
        				font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        			}
        			.invoice-box.rtl table {
        				text-align: right;
        			}
        			.invoice-box.rtl table tr td:nth-child(2) {
        				text-align: left;
        			}
        		</style>
        	</head>
        	<body>
        		<div class="invoice-box">
        			<table cellpadding="0" cellspacing="0">
        				<tr class="top">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td class="title">
        									<img src="https://png.pngtree.com/png-vector/20190830/ourmid/pngtree-crossed-spoon-and-fork-restaurant-and-food-logo-design-png-image_1716397.jpg" style="width: 100%; max-width: 300px" />
        								</td>
        								<td>
                                          <table>
                                            <tr class>
                                              <td class="invoiceid">Invoice ID</td>
                                            </tr>
                                            <tr>
                                              <td class="idno">""" + str(order_to_delete.id) + """</td>
                                            </tr>
                                          </table>
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>
        				<tr class="information">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td>
        									Canteen<br />
        									e-Campus<br />
        									Thane 400607
        								</td>
        							<td>
        									<br />
        									<br />
        									9372642011
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>
        				<tr class="heading">
        					<td>Payment Method</td>
        				</tr>
        				<tr class="details">
        					<td>Offline</td>
        				</tr>
        				<tr class="heading">
        					<td>Item</td>
        				</tr>
        				<tr class="items">
        					<td>""" + order_to_delete.order_desc + """</td>
        				</tr>
        			</table>
        		</div>
        	</body>
        </html>
        """
        connection.starttls()
        connection.ehlo()
        connection.login(user=my_email, password=password)
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(message, 'html'))
        msg['Subject'] = f'Order id {order_to_delete.id} has been prepared'
        msg['From'] = my_email
        msg['To'] = order_to_delete.author.email
        connection.sendmail(
            from_addr=my_email,
            to_addrs=order_to_delete.author.email,
            msg=msg.as_string()
        )
    db.session.delete(order_to_delete)
    db.session.commit()
    return redirect(url_for('view_orders'))


@app.route("/canteen", methods=["GET", "POST"])
def canteen():
    items = Menu.query.all()
    if current_user.is_authenticated:
        if request.method == "POST":
            order_desc = ""
            qty = request.form.getlist("qty")
            item_price = request.form.getlist("item_price")
            item_name = request.form.getlist("item_name")
            for i in range(len(item_name)):
                if qty[i] != "0":
                    order_desc += f"{item_name[i]} x{qty[i]} -> Rs {int(qty[i]) * float(item_price[i])}\n"
            new_order = Order(
                author_id=current_user.id,
                order_desc=order_desc
            )
            db.session.add(new_order)
            db.session.commit()
            flash(f"Your order id {new_order.id} has been received and will be prepared soon!", "success")
            return redirect(url_for("canteen"))
    else:
        flash("You need to login first!")
        return redirect("/login")
    return render_template("canteen.html", items=items)


@app.route("/canteen_admin", methods=["GET", "POST"])
def view_orders():
    orders = Order.query.all()
    return render_template("canteen_orders.html", orders=orders)


@login_required
@app.route("/new-lostfound", methods=["GET", "POST"])
def add_lostfound():
    form = LostFoundForm()
    if form.validate_on_submit():
        new_post = LostFound(
            title=form.title.data,
            user_choice=form.user_choice.data,
            author_id=current_user.id,
            item_desc=form.item_desc.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_items"))
    return render_template("lost_found.html", form=form)


@app.route('/lostfound')
def get_all_items():
    posts = LostFound.query.all()
    return render_template("indexlostfound.html", all_posts=posts)


@app.route("/lost_found/<int:item_id>", methods=["GET", "POST"])
def lost_found(item_id):
    if current_user.is_authenticated:
        items = LostFound.query.get(item_id)
        form = CommentForm()
        if form.validate_on_submit():
            new_comment = LostFoundComment(
                comment=form.comment.data,
                author_id=current_user.id,
                post_id=items.id
            )
            db.session.add(new_comment)
            db.session.commit()
        return render_template("show_lostfound.html", post=items, form=form)

    return redirect("/login")


@login_required
@app.route("/del_lost_found/<int:item_id>")
def delete_item(item_id):
    item_to_delete = LostFound.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_items'))


@login_required
@app.route("/make-stackpost", methods=["GET", "POST"])
def add_new_stack_post():
    form = StackQuesForm()
    if form.validate_on_submit():
        new_stack_post = StackPost(
            title=form.title.data,
            question=form.question.data,
            user_choice=form.user_choice.data,
            date=date.today().strftime("%B %d, %Y"),
            stack_author=current_user
        )
        db.session.add(new_stack_post)
        db.session.commit()
        return redirect(url_for("get_all_stack_posts"))
    return render_template("make-stack-post.html", form=form)


@app.route("/stackoverflow")
def get_all_stack_posts():
    posts = StackPost.query.all()
    return render_template("stackoverflow.html", all_posts=posts)


@app.route("/stackpost/<int:stackpost_id>", methods=["GET", "POST"])
def show_stackpost(stackpost_id):
    requested_stackpost = StackPost.query.get(stackpost_id)
    form = CommentFormStack()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            new_stack_comment = StackComment(
                comment=form.comment.data,
                stack_comment_author=current_user,
                stack_parent_post=requested_stackpost
            )
            db.session.add(new_stack_comment)
            db.session.commit()
        return render_template("stackpost.html", post=requested_stackpost, form=form)
    return render_template("stackpost.html", post=requested_stackpost, form=form)


@login_required
@app.route("/edit-stackpost/<int:stackpost_id>", methods=["GET", "POST"])
def edit_stackpost(stackpost_id):
    post = StackPost.query.get(stackpost_id)
    edit_stackform = StackQuesForm(
        title=post.title,
        question=post.question,
        user_choice=post.user_choice,
        stack_author=post.stack_author,
    )
    if edit_stackform.validate_on_submit():
        post.title = edit_stackform.title.data
        post.question = edit_stackform.question.data
        post.user_choice = edit_stackform.user_choice.data
        post.stack_author = current_user
        post.date = date.today().strftime("%B %d, %Y")
        db.session.commit()
        return redirect(url_for("show_stackpost", stackpost_id=post.id))

    return render_template("make-stack-post.html", form=edit_stackform, is_edit=True)


@login_required
@app.route("/delete-stackpost/<int:stackpost_id>", methods=["GET", "POST"])
def delete_stackpost(stackpost_id):
    post_to_delete = StackPost.query.get(stackpost_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_stack_posts'))


@app.route("/projectoverflow")
def get_all_projects():
    post = ProjectPost.query.all()
    return render_template("projectoverflow.html", all_posts=post)


@login_required
@app.route("/new-project-post", methods=["GET", "POST"])
def add_new_project():
    form = ProjectPostForm()
    if form.validate_on_submit():
        new_project = ProjectPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            project_author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            user_choice=form.user_choice.data
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("get_all_projects"))
    return render_template("make-project-post.html", form=form)


@app.route("/projectpost/<int:projectpost_id>", methods=["GET", "POST"])
def show_projectpost(projectpost_id):
    requested_projectpost = ProjectPost.query.get(projectpost_id)
    form = CommentFormProject()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            new_project_comment = ProjectComment(
                comment=form.comment.data,
                project_comment_author=current_user,
                project_parent_post=requested_projectpost
            )
            db.session.add(new_project_comment)
            db.session.commit()
        return render_template("projectpost.html", post=requested_projectpost, form=form)
    return render_template("projectpost.html", post=requested_projectpost, form=form)


@login_required
@app.route("/edit-project/<int:projectpost_id>", methods=["GET", "POST"])
def edit_projectpost(projectpost_id):
    post = ProjectPost.query.get(projectpost_id)
    edit_projectform = ProjectPostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        img_url=post.img_url,
        project_author=current_user,
        date=date.today().strftime("%B %d, %Y"),
        user_choice=post.user_choice
    )
    if edit_projectform.validate_on_submit():
        post.title = edit_projectform.title.data
        post.subtitle = edit_projectform.subtitle.data
        post.body = edit_projectform.body.data
        post.project_author = current_user
        post.date = date.today().strftime("%B %d, %Y")
        post.user_choice = edit_projectform.user_choice
        post.img_url = edit_projectform.img_url
        db.session.commit()
        return redirect(url_for("show_projectpost", projectpost_id=post.id))

    return render_template("make-project.html", form=edit_projectform, is_edit=True)


@login_required
@app.route("/delete-projectpost/<int:projectpost_id>", methods=["GET", "POST"])
def delete_projectpost(projectpost_id):
    post_to_delete = ProjectPost.query.get(projectpost_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_projects'))


if __name__ == "__main__":
    app.run(debug=True)
