import pytz
from task import celery
from util import logger
from datetime import datetime
from db.model import Invitation
from db.service import InvitationService, UserService
from mail import MailSendService
from util.hash import Hash


@celery.task(serializer='json')
def invitation_task(user_id, emails):
    """
    Invite users by using e-mail addresses

    :param int user_id: invitation sender
    :param list[str] emails: list of e-mail addresses who wanted to invite
    """
    logger.info('Task creating')

    ins = InvitationService()
    ms = MailSendService()
    us = UserService()

    # get user by user id
    user = us.get_by_id(user_id)

    for email in emails:
        # get invitation by e-mail address
        i = ins.get_by_email(email)
        if i is not None:
            logger.info(f'The {email} already invited.')
            continue

        i = Invitation()
        i.user_id = user_id
        i.email = email
        i.code = Hash.uuid()
        i.create_time = datetime.now(tz=pytz.UTC)

        # create new invitation
        ins.create(i)

        subject = 'Your have an invitation - Spectrome'
        text = f'''
        Our user { user.name } ({ user.username }) has been sent an invitation to you.

        Please click the button bellow to join in our community.

        https://spectrome.app/users/invite/accept?code={ i.code }
        '''

        # create html content
        html = ms.get_template(
            name='user_invitation.html',
            email=i.email,
            realname=user.name,
            username=user.username,
            code=i.code,
        )

        # send e-mail
        ms.send(email, subject, text.strip(), html.strip())

    logger.info('Invitation e-mail(s) has been sent.')
