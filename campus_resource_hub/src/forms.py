"""
WTForms for the application.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    """Login form with CSRF protection."""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """Registration form for new users."""
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    role = SelectField('Role', choices=[('student', 'Student'), ('staff', 'Staff'), ('admin', 'Admin')], validators=[DataRequired()], default='student')

class BookingForm(FlaskForm):
    """Booking form with CSRF protection."""
    start_date = StringField('Start Date', validators=[DataRequired()], 
                            render_kw={"type": "datetime-local"})
    end_date = StringField('End Date', validators=[DataRequired()], 
                          render_kw={"type": "datetime-local"})
    notes = TextAreaField('Notes', validators=[Optional()])
    recurrence_type = SelectField('Repeat', choices=[
        ('', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], validators=[Optional()], default='')
    recurrence_end_date = StringField('Repeat Until', validators=[Optional()],
                                     render_kw={"type": "datetime-local"})
    
    def validate_recurrence_end_date(self, field):
        """Validate recurrence end date if recurrence is selected."""
        if self.recurrence_type.data and field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['recurrence_end_date'] = parsed
                
                # Validate that recurrence end date is after start date
                if hasattr(self, '_parsed_dates') and 'start_date' in self._parsed_dates:
                    if parsed <= self._parsed_dates['start_date']:
                        from wtforms.validators import ValidationError
                        raise ValidationError('Repeat until date must be after start date.')
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format. Please use the date picker.')
        elif self.recurrence_type.data and not field.data:
            from wtforms.validators import ValidationError
            raise ValidationError('Please specify when the recurrence should end.')
    
    @property
    def parsed_recurrence_end_date(self):
        """Get parsed recurrence end date."""
        return getattr(self, '_parsed_dates', {}).get('recurrence_end_date')
    
    def validate_start_date(self, field):
        """Validate and parse start date."""
        if field.data:
            try:
                # Parse datetime-local format: YYYY-MM-DDTHH:MM
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                # Store parsed date for use in controller
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['start_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format. Please use the date picker.')
    
    def validate_end_date(self, field):
        """Validate and parse end date."""
        if field.data:
            try:
                # Parse datetime-local format: YYYY-MM-DDTHH:MM
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                # Store parsed date for use in controller
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['end_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format. Please use the date picker.')
    
    @property
    def parsed_start_date(self):
        """Get parsed start date."""
        return getattr(self, '_parsed_dates', {}).get('start_date')
    
    @property
    def parsed_end_date(self):
        """Get parsed end date."""
        return getattr(self, '_parsed_dates', {}).get('end_date')


class MessageForm(FlaskForm):
    """Form to compose a message."""
    recipient = StringField('To (username or email)', validators=[DataRequired(), Length(max=120)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    body = TextAreaField('Message', validators=[DataRequired()])


class ProfileForm(FlaskForm):
    """Form to update profile details."""
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])


class PasswordChangeForm(FlaskForm):
    """Form to change password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])


class AdminUserForm(FlaskForm):
    """Admin form to create/edit users."""
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)], 
                             description='Required when creating a new user. Leave blank when editing to keep existing password.')
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    role = SelectField('Role', choices=[('student', 'Student'), ('staff', 'Staff'), ('admin', 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)


class AdminResourceForm(FlaskForm):
    """Admin form to create/edit resources."""
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    category = StringField('Category', validators=[DataRequired(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=255)])
    capacity = StringField('Capacity', validators=[Optional()])
    owner_id = SelectField('Owner', validators=[Optional()], coerce=int, choices=[])
    is_available = BooleanField('Available', default=True)
    is_featured = BooleanField('Featured', default=False)
    requires_approval = BooleanField('Requires Approval', default=False, description='Bookings for this resource will require admin approval')
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], validators=[DataRequired()], default='draft')
    equipment = TextAreaField('Equipment List', validators=[Optional()], description='Enter equipment items separated by commas (e.g., Projector, Whiteboard, Microphone)')
    images = FileField('Upload Images', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')], render_kw={"multiple": True})


class AdminBookingForm(FlaskForm):
    """Admin form to create/edit bookings."""
    user_id = SelectField('User', validators=[DataRequired()], coerce=int)
    resource_id = SelectField('Resource', validators=[DataRequired()], coerce=int)
    start_date = StringField('Start Date', validators=[DataRequired()], 
                            render_kw={"type": "datetime-local"})
    end_date = StringField('End Date', validators=[DataRequired()], 
                          render_kw={"type": "datetime-local"})
    status = SelectField('Status', choices=[('pending', 'Pending'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    recurrence_type = SelectField('Recurrence Type', choices=[
        ('', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], validators=[Optional()], default='')
    recurrence_end_date = StringField('Recurrence End Date', validators=[Optional()],
                                     render_kw={"type": "datetime-local"})
    
    def validate_start_date(self, field):
        """Validate and parse start date."""
        if field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['start_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format.')
    
    def validate_end_date(self, field):
        """Validate and parse end date."""
        if field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['end_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format.')
    
    def validate_recurrence_end_date(self, field):
        """Validate recurrence end date if recurrence is selected."""
        if self.recurrence_type.data and field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['recurrence_end_date'] = parsed
                
                # Validate that recurrence end date is after start date
                if hasattr(self, '_parsed_dates') and 'start_date' in self._parsed_dates:
                    if parsed <= self._parsed_dates['start_date']:
                        from wtforms.validators import ValidationError
                        raise ValidationError('Recurrence end date must be after start date.')
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format. Please use the date picker.')
        elif self.recurrence_type.data and not field.data:
            from wtforms.validators import ValidationError
            raise ValidationError('Please specify when the recurrence should end.')
    
    @property
    def parsed_start_date(self):
        return getattr(self, '_parsed_dates', {}).get('start_date')
    
    @property
    def parsed_end_date(self):
        return getattr(self, '_parsed_dates', {}).get('end_date')
    
    @property
    def parsed_recurrence_end_date(self):
        """Get parsed recurrence end date."""
        return getattr(self, '_parsed_dates', {}).get('recurrence_end_date')


class WaitlistForm(FlaskForm):
    """Form to join waitlist."""
    start_date = StringField('Start Date', validators=[DataRequired()], 
                            render_kw={"type": "datetime-local"})
    end_date = StringField('End Date', validators=[DataRequired()], 
                          render_kw={"type": "datetime-local"})
    notes = TextAreaField('Notes', validators=[Optional()])
    
    def validate_start_date(self, field):
        """Validate and parse start date."""
        if field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['start_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format.')
    
    def validate_end_date(self, field):
        """Validate and parse end date."""
        if field.data:
            try:
                parsed = datetime.strptime(field.data, '%Y-%m-%dT%H:%M')
                if not hasattr(self, '_parsed_dates'):
                    self._parsed_dates = {}
                self._parsed_dates['end_date'] = parsed
            except ValueError:
                from wtforms.validators import ValidationError
                raise ValidationError('Invalid date format.')
    
    @property
    def parsed_start_date(self):
        return getattr(self, '_parsed_dates', {}).get('start_date')
    
    @property
    def parsed_end_date(self):
        return getattr(self, '_parsed_dates', {}).get('end_date')


class ReviewForm(FlaskForm):
    """Form to create/edit a review."""
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], 
                        coerce=int, validators=[DataRequired(), NumberRange(min=1, max=5, message='Rating must be between 1 and 5')])
    review_text = TextAreaField('Review', validators=[Optional(), Length(max=1000)])

class CancelBookingForm(FlaskForm):
    """Simple form for cancelling bookings with CSRF protection."""
    pass

