from db import get_session
from db.model import Invitation


class InvitationService:
    def get_by_email(self, email):
        """
        Get invitation by e-mail address

        :param str email: e-mail address
        :return: invitation instance
        :rtype: db.model.Invitation or None
        """
        session = get_session()

        try:
            return session.query(Invitation).filter(Invitation.email == email).first()
        finally:
            session.close()

    def create(self, invitation):
        """
        Create new invitation on the database

        :param User user: invitation instance
        """
        session = get_session()

        try:
            session.add(invitation)
            session.commit()
            session.refresh(invitation)
        finally:
            session.close()
