from task import celery
from db.model import UserStatus
from db.service import UserService
from mail import MailSendService
from util import logger


@celery.task(serializer='json')
def create_account_task(user_id):
    """
    Prepare and send e-mail to new created account.

    :param int user_id: user identity
    """
    us = UserService()

    # get user by user id
    user = us.get_by_id(user_id)
    if user is None:
        return

    ms = MailSendService()

    subject = 'Your account created successfully - Spectrome'

    text = f'''
    Your account created.

    We need to verify this e-mail address.
    Please write the code in the application.

    Here is your code: {user.code}
    '''

    # create html content
    html = ms.get_template(
        name='create_account.html',
        email=user.email,
        realname=user.name,
        code=user.code,
    )

    logger.info('Account create mail sending')

    # send e-mail
    ms.send(user.email, subject, text.strip(), html.strip())

    # update upser status
    user.status = UserStatus.ACTIVATION_WAIT
    us.update(user)

    logger.info('Account status updated')
