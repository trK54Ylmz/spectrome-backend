from task import celery
from util import logger
from db.service import ForgotService, UserService
from mail import MailSendService


@celery.task(serializer='json')
def forgot_task(user_id):
    """
    Send forgot password mail

    :param int user_id: user primary key
    """
    logger.info('Task creating')

    fs = ForgotService()
    ms = MailSendService()
    us = UserService()

    # get user by user id
    user = us.get_by_id(user_id)
    forgot = fs.get_by_user_id(user_id)

    subject = 'Forgot password - Spectrome'
    text = f'''
    We need to verify forgot request.

    Please write the code in the application.

    Here is your code: {forgot.code}
    '''

    # create html content
    html = ms.get_template(
        name='forgot_password.html',
        email=user.email,
        realname=user.name,
        code=forgot.code,
    )

    # send e-mail
    ms.send(user.email, subject, text.strip(), html.strip())

    logger.info('Forgot e-mail has been sent.')
