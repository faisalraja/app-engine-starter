import logging
import config
from lib import utils
from lib.basehandler import BaseHandler
import sendgrid
from lib import email_template
from sendgrid.helpers.mail import *


__author__ = 'faisal'


class EmailHandler(BaseHandler):

    def _compose_message(self, message, data):

        data['messages'] = [map(lambda m: m.format(**data), msg) for msg in message]
        data['project_name'] = config.project_name

        return {
            'text': '\n'.join([m[1] for m in data['messages']]),
            'html': self.jinja2.render_template('main/email.html', **data)
        }

    def send(self, template, data):

        logging.debug('Template: {}\nData: {}'.format(template, data))
        message = self._compose_message(template['content'], data)
        subject = template['subject'].format(**data)
        logging.debug('Subject: {}\nText: {}'.format(subject, message['text']))

        sg = sendgrid.SendGridAPIClient(apikey=config.sendgrid['api_key'])
        to_email = None

        if config.is_production or data['to'] in config.allowed_dev_email_recipients:
            to_email = Email(data['to'])

        content = Content('text/plain', message['text'])

        m = Mail(Email(data.get('from', config.sendgrid['from_email'])), subject, to_email, content)
        m.add_content(Content('text/html', message['html']))

        if to_email:
            response = sg.client.mail.send.post(request_body=m.get())
            logging.debug('SendGrid Response: {} {}'.format(response.status_code, response.body))

    def post(self):
        template = self.request.get('template')
        callback = self.request.get('callback')
        params = json.loads(self.request.get('params'))

        if not hasattr(email_template, template):
            logging.error('Template: {} not found in email_template module'.format(template))
        elif not hasattr(email_template, callback):
            logging.error('Callback: {} not found in email_template module'.format(callback))
        else:
            tpl = getattr(email_template, template)
            data = getattr(email_template, callback)(**params)

            if not utils.is_valid_email(data.get('to')):
                logging.error('Email: {} is not valid')
            else:
                self.send(tpl, data)

    def get(self):
        params = {
            'messages': email_template.verify_email['content']
        }

        self.render_template('main/email.html', **params)
