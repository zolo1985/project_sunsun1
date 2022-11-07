from flask import Blueprint, send_file, send_from_directory
from google.cloud import storage
import tempfile
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('webapp/keys.json')
supplier1_util_blueprint = Blueprint('supplier1_util', __name__)

@supplier1_util_blueprint.route('/artwork/<string:artwork>')
def artwork(artwork):
    if artwork:
        client = storage.Client(project='project-sunsun', credentials=credentials)
        bucket = client.get_bucket('sunsun_bucket')
        blob = bucket.blob('{0}/'.format(artwork) + '{0}'.format(artwork) + '_300x300.jpg')
        if blob is not None:
            with tempfile.NamedTemporaryFile() as temp:
                blob.download_to_filename(temp.name)
                return send_file(temp.name, attachment_filename=artwork, as_attachment=False, mimetype='image/jpg')
    else:
        return send_from_directory(directory='static/images', filename='placeholder.jpg')