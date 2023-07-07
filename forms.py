from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FileField, DateField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreateEventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Event Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Event Content", validators=[DataRequired()])
    submit = SubmitField("Create")


class RegisterForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Your response about this", validators=[DataRequired()])
    submit = SubmitField("Comment")


class LostFoundForm(FlaskForm):
    choices = ["Lost", "Found"]
    user_choice = SelectField("Choose one", choices=choices, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    item_desc = CKEditorField(f"Tell something about the item , enter your desired way of contact",
                              validators=[DataRequired()])
    submit = SubmitField("Post")


class QAForm(FlaskForm):
    question = CKEditorField(f"Tell something about the problem you are facing!", validators=[DataRequired()])
    submit = SubmitField("Post")


class GrievanceForm(FlaskForm):
    choices = ["Cleanliness", "Fees", "Ragging", "Other"]
    user_choice = SelectField("Type of issue", choices=choices, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_no = StringField("Phone number")
    grievance = CKEditorField("Tell us about your issue", validators=[DataRequired()])
    submit = SubmitField("Post")


class AttendanceForm(FlaskForm):
    attendancesheet = FileField("Upload the excel sheet")
    attendancedate = DateField("Date of the attendacnce sheet")
    submit = SubmitField("Post")


class StackQuesForm(FlaskForm):
    title = StringField("What is the topic", validators=[DataRequired()])
    question = CKEditorField("Explain Your doubts")
    choices = ["c", "python", "java", "c++", "Other"]
    user_choice = SelectField("Language", choices=choices, validators=[DataRequired()])
    submit = SubmitField("Submit")


class CommentFormStack(FlaskForm):
    comment = CKEditorField("Solve the doubt", validators=[DataRequired()])
    submit = SubmitField("Comment")


class CommentFormProject(FlaskForm):
    comment = CKEditorField("Your views", validators=[DataRequired()])
    submit = SubmitField("Comment")


class ProjectPostForm(FlaskForm):
    title = StringField("Project title", validators=[DataRequired()])
    subtitle = StringField("Brief", validators=[DataRequired()])
    body = CKEditorField("Project description", validators=[DataRequired()])
    img_url = StringField("Event Image URL", validators=[URL()])
    choices = ["F.E", "S.E", "T.E", "B.E"]
    user_choice = SelectField("Academic year", choices=choices, validators=[DataRequired()])
    submit = SubmitField("Create")


class MarksForm(FlaskForm):
    file = FileField("Upload student's marks file.")
    submit = SubmitField("Upload")
