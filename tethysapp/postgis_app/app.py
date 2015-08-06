from tethys_apps.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore

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
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='postgis-app',
                           controller='postgis_app.controllers.home'),
                    UrlMap(name='flood',
                           url='postgis-app/flood',
                           controller='postgis_app.controllers.flood'),
                    UrlMap(name='flooded_addresses',
                           url='postgis-app/flooded-addresses/{id}',
                           controller='postgis_app.controllers.flooded_addresses'),
                    UrlMap(name='list',
                           url='postgis-app/flooded-addresses/{id}/list',
                           controller='postgis_app.controllers.list'),
        )

        return url_maps

    def persistent_stores(self):
        """
        Add one or more persistent_stores.
        """
        # Create a new persistent store (database)
        stores = (PersistentStore(name='flooded_addresses',
                                  initializer='init_stores:init_flooded_addresses_db',
                                  spatial=True
                  ),
        )

        return stores