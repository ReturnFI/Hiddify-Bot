# api.py
import requests
from datetime import datetime
import uuid
import qrcode
from io import BytesIO
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from dotenv import load_dotenv
import os


load_dotenv()
ALLOWED_USER_IDS = [int(id) for id in os.getenv("ALLOWED_USER_IDS", "").split(",")]
ADMIN_UUID = os.getenv("ADMIN_UUID")
ADMIN_URLAPI = os.getenv("ADMIN_URLAPI")
SUBLINK_URL = os.getenv("SUBLINK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

class HiddifyApi:
    def __init__(self):
        self.admin_secret = ADMIN_UUID
        self.base_url = f"{ADMIN_URLAPI}"
        self.allowed_user_ids = ALLOWED_USER_IDS
        self.telegram_token = TELEGRAM_TOKEN
        self.sublinkurl = SUBLINK_URL

    def authenticate(self):
        return (ADMIN_UUID, '')

    def generate_uuid(self) -> str:
        """Generate a UUID."""
        return str(uuid.uuid4())

    def get_system_status(self) -> dict:
        """Get the system status."""
        try:
            response = requests.get(f"{self.base_url}/api/v2/admin/server_status/", auth=self.authenticate())
            data = response.json()
            stats = data.get("stats", {})
            usage_history = data.get("usage_history", {})
            stats["usage_history"] = usage_history
            return stats
        except requests.RequestException as e:
            print(f"Error in get_system_status: {e}")
            return {}

    def make_post_request(self, endpoint: str, json_data: dict) -> bool:
        """Make a POST request."""
        try:
            response = requests.post(endpoint, json=json_data, auth=self.authenticate())
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error in making POST request: {e}")
            return False

    def make_patch_request(self, endpoint: str, json_data: dict) -> bool:
        """Make a PATCH request."""
        try:
            response = requests.patch(endpoint, json=json_data, auth=self.authenticate())
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error in making PATCH request: {e}")
            return False

    def get_admin_list(self) -> list:
        """Get the list of users."""
        try:
            response = requests.get(f"{self.base_url}/api/v2/admin/admin_user/", auth=self.authenticate())
            return response.json()
        except requests.RequestException as e:
            print(f"Error in get_admin_list: {e}")
            return []

    def delete_admin_user(self, uuid: str) -> bool:
        """Delete a user."""
        try:
            endpoint = f"{self.base_url}/api/v2/admin/admin_user/{uuid}/"
            response = requests.delete(endpoint, auth=self.authenticate())
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error in delete_admin_user: {e}")
            return False

    def add_service(self, uuid: str, comment: str, name: str, day: int, traffic: float, telegram_id: int) -> bool:
        """Add a new service."""
        if telegram_id not in self.allowed_user_ids:
            print("Unauthorized user tried to add a service.")
            return False

        data = {
            "added_by_uuid": self.admin_secret,
            "comment": comment,
            "current_usage_GB": 0,
            "mode": "no_reset",
            "name": name,
            "package_days": day,
            "telegram_id": None,
            "usage_limit_GB": traffic,
            "uuid": uuid,
        }

        endpoint = f"{self.base_url}/api/v2/admin/user/"
        return self.make_post_request(endpoint, data)

    def get_user_list(self) -> list:
        """Get the list of users."""
        try:
            response = requests.get(f"{self.base_url}/api/v2/admin/user/", auth=self.authenticate())
            return response.json()
        except requests.RequestException as e:
            print(f"Error in get_user_list: {e}")
            return []

    def get_user_list_name(self, query_name) -> list:
        """Get the list of users and filter by name containing the query."""
        try:
            response = requests.get(f"{self.base_url}/api/v2/admin/user/", auth=self.authenticate())
            user_list = response.json()
            filtered_users = [user for user in user_list if query_name.lower() in user.get('name', '').lower()]
            return filtered_users
        except requests.RequestException as e:
            print(f"Error in get_user_list_name: {e}")
            return []
    
    def tele_id(self, uuid: str, telegram_id: int) -> bool:
        """Add Telegram ID."""
        data = {
            "telegram_id": telegram_id
        }
        endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
        return self.make_patch_request(endpoint, data)

    def reset_user_last_reset_time(self, uuid: str) -> bool:
        """Reset the user's last reset time."""
        try:
            user_data = self.find_service(uuid)
            if not user_data:
                print("User not found.")
                return False
            user_data['last_reset_time'] = datetime.now().strftime('%Y-%m-%d')
            user_data['start_date'] = None
            user_data['current_usage_GB'] = 0
            endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
            return self.make_patch_request(endpoint, user_data)
        except requests.RequestException as e:
            print(f"Error in reset_user_last_reset_time: {e}")
            return False

    def update_package_days(self, uuid: str) -> bool:
        """Update the package days for a user."""
        try:
            user_data = self.find_service(uuid)
            if not user_data:
                print("User not found.")
                return False
            user_data['last_reset_time'] = datetime.now().strftime('%Y-%m-%d')
            user_data['start_date'] = None
            endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
            return self.make_patch_request(endpoint, user_data)
        except requests.RequestException as e:
            print(f"Error in update_package_days: {e}")
            return False

    def update_traffic(self, uuid: str) -> bool:
        """Reset the traffic limit for a user to 0."""
        try:
            user_data = self.find_service(uuid)
            if not user_data:
                print("User not found.")
                return False
            user_data['current_usage_GB'] = 0
            endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
            return self.make_patch_request(endpoint, user_data)
        except requests.RequestException as e:
            print(f"Error in update_traffic: {e}")
            return False

    def delete_user(self, uuid: str) -> bool:
        """Delete a user."""
        try:
            endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
            response = requests.delete(endpoint, auth=self.authenticate())
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error in delete_user: {e}")
            return False

    def find_service(self, uuid: str, name: str = None) -> dict:
        """Find a service by UUID and optional name."""
        try:
            response = requests.get(f"{self.base_url}/api/v2/admin/user/{uuid}/", auth=self.authenticate())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"User with UUID {uuid} not found.")
                return {}
        except requests.RequestException as e:
            print(f"Error in find_service: {e}")
            return {}


    def backup_file(self) -> bytes:
        """Backup the file."""
        try:
            response = requests.get(f"{self.base_url}/admin/backup/backupfile/", auth=self.authenticate())
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to retrieve backup file. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error in backup_file: {e}")
            return None

    def get_app_information(self, uuid: str) -> dict:
        """Get information about available apps for a given UUID."""
        try:
            url = f"{self.sublinkurl}/{uuid}/api/v2/user/apps/"
            querystring = {"platform": "all"}
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers, params=querystring)
            
            if response.status_code == 200:
                return response.json()
            else:
                print("Failed to fetch app information. Status code:", response.status_code)
                return {}
        except requests.RequestException as e:
            print(f"Error in get_app_information: {e}")
            return {}

    def generate_qr_code(self, data: str) -> BytesIO:
        """Generate a QR code for the given data."""
        qr = qrcode.QRCode(
            version=1,
            box_size=6,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color="black",
            back_color="white",
            image_factory=StyledPilImage,
            module_drawer=SquareModuleDrawer(),
            color_mask=SolidFillColorMask()
        )

        qr_byte_io = BytesIO()
        qr_img.save(qr_byte_io, format='PNG', optimize=True)
        qr_byte_io.seek(0)
        
        return qr_byte_io
