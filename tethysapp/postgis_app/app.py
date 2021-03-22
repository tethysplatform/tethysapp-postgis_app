from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting


class PostgisApp(TethysAppBase):
    """
    Tethys app class for PostGIS App.
    """

    name = 'PostGIS App'
    index = 'postgis_app:home'
    icon = 'postgis_app/images/icon.gif'
    package = 'postgis_app'
    root_url = 'postgis-app'
    color = '#e74c3c'
    description = ''
    tags = []
    enable_feedback = False
    feedback_emails = []
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(name='home',
                   url='postgis-app',
                   controller='postgis_app.controllers.home'),
            UrlMap(name='flood',
                   url='postgis-app/flood',
                   controller='postgis_app.controllers.flood'),
            UrlMap(name='flooded_addresses',
                   url='postgis-app/flooded-addresses/{url_id}',
                   controller='postgis_app.controllers.flooded_addresses'),
            UrlMap(name='list',
                   url='postgis-app/flooded-addresses/{url_id}/list',
                   controller='postgis_app.controllers.list_flooded_addresses'),
        )

        return url_maps

    def persistent_store_settings(self):
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='flooded_addresses',
                description='PostGIS database',
                initializer='postgis_app.model.init_flooded_addresses_db',
                spatial=True,
                required=True
            ),
        )

        return ps_settings
