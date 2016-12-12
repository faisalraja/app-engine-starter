import config


# Email Templates for outgoing emails

verify_email = {
    'subject': 'Verify Email',
    'content': (
        ('p', 'Hi {name},'),
        ('p', ''),
        ('p', 'Click the button below to verify your {} account.'.format(config.project_name)),
        ('button', '{link}', 'Verify Account')
    )
}

forgot_pass = {
    'subject': 'Forgot Password',
    'content': (
        ('p', 'Hi {name},'),
        ('p', ''),
        ('p', 'You have requested to reset your password.'),
        ('p', 'Click the button below to reset password.'),
        ('button', '{link}', 'Reset Password')
    )
}


# Email Template data processor for generating tokens etc

def default(**kwargs):
    """Must return a to: email as minimum requirements"""
    return kwargs


def generate_user_token():

    return