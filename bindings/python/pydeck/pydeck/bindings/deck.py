import os
import warnings

from .json_tools import JSONMixin
from .layer import Layer
from .view import View
from .view_state import ViewState
from ..io.html import deck_to_html
from ..widget import DeckGLWidget


class Deck(JSONMixin):
    """The renderer and configuration for a visualization"""
    def __init__(
        self,
        layers=[],
        views=[View()],
        map_style='mapbox://styles/mapbox/dark-v9',
        mapbox_key=None,
        initial_view_state=ViewState(),
    ):
        """Constructor for a Deck object, similar to the `Deck`_ class from deck.gl

        Requires a Mapbox API token to display a basemap, see notes below.

        Parameters
        ----------
        layers : :obj:`pydeck.Layer` or :obj:`list` of :obj:`pydeck.Layer`, default []
            List of pydeck.Layer objects to render
        views : :obj:`list` of :obj:`pydeck.View`, default [pydeck.View()]
            List of `pydeck.View` objects to render
        map_style : str, default "mapbox://styles/mapbox/dark-v9"
            URI for Mapbox basemap style
        initial_view_state : pydeck.ViewState, default pydeck.ViewState()
            Initial camera angle relative to the map, defaults to a fully zoomed out 0, 0-centered map
            To compute a viewport from data, see `pydeck.data_utils.autocompute_viewport`
        mapbox_key : str, default None
            Read on inititialization from the MAPBOX_API_KEY environment variable. Defaults to None if not set.
            See https://docs.mapbox.com/help/how-mapbox-works/access-tokens/#mapbox-account-dashboard

        .. _Deck:
            https://deck.gl/#/documentation/deckgl-api-reference/deck
        """
        self.layers = []
        if isinstance(layers, Layer):
            self.layers.append(layers)
        else:
            self.layers = layers
        self.views = views
        self.map_style = map_style
        # Use passed view state
        self.initial_view_state = initial_view_state
        self.deck_widget = DeckGLWidget()
        self.mapbox_key = mapbox_key or os.getenv('MAPBOX_API_KEY')
        self.deck_widget.mapbox_key = self.mapbox_key
        if not self.mapbox_key:
            warnings.warn(
                'Mapbox API key is not set. This may impact available features of pydeck.', UserWarning)

    def __add__(self, obj):
        """
        Override of the addition operator to add attributes to the Deck object

        Parameters
        ----------
        obj : object
            pydeck.Layer, pydeck.View, or pydeck.ViewState

        Examples
        --------
        >>> pydeck.Deck() + pydeck.View(controller=False)
        >>> pydeck.Deck()
        {"initialViewState": {"bearing": 0, ... , "views": [{"controller": false, "type": "MapView"}}... }
        """
        if isinstance(obj, Layer):
            self.layers.append(obj)
        elif isinstance(obj, View):
            self.views = [obj]
        elif isinstance(obj, ViewState):
            self.initial_view_state = obj
        else:
            obj_type = type(obj).__name__
            raise TypeError("Cannot join object of type", obj_type)

    def show(self):
        """Displays current Deck object for a Jupyter notebook"""
        self.update()
        return self.deck_widget

    def update(self):
        """Updates a deck.gl map to reflect the current state of the configuration

        For example, if you've modified data passed to Layer and rendered the map using `.show()`,
        you can call `update` to pass the new configuration to the map

        Intended for use in a Jupyter notebook
        """
        self.deck_widget.json_input = self.to_json()

    def to_html(self, filename=None, open_browser=False):
        """Writes a file and loads it to an iframe, if in a Jupyter notebook
        Otherwise writes a file and optionally opens it in a web browser

        Parameters
        ----------
        filename : str, default None
            Name of the file. If no name is provided, a randomly named file will be written locally.
        open_browser : bool, default False
            Whether a browser window will open or not after write
        """
        deck_to_html(self.to_json(), self.mapbox_key)
