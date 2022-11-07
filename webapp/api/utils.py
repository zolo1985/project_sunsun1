import tempfile

from flask import Blueprint, send_file, send_from_directory
from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('webapp/keys.json')

utils_api = Blueprint('utils_api', __name__)

@utils_api.route('/api/image/<string:artwork>')
def article_image(artwork):
    if artwork:
        client = storage.Client(
            project='project-sunsun', credentials=credentials)
        bucket = client.get_bucket('sunsun_bucket')
        blob = bucket.blob('{0}/'.format(artwork) + '{0}'.format(artwork) + '_300x300.jpg')
        if blob is not None:
            with tempfile.NamedTemporaryFile() as temp:
                blob.download_to_filename(temp.name)
                return send_file(temp.name, as_attachment=False, attachment_filename=artwork, mimetype='image/jpg')
    else:
        return send_from_directory(directory='static/images', filename='placeholder.jpg', as_attachment=False)