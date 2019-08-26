from urllib.parse import urljoin

from stac_api import ConfigLoader

from satstac import Collection, Item


class LinkEncoder(object):

    def __init__(self, asset, type, endpoint):
        self.asset = asset
        self.type = type
        self.endpoint = endpoint
        self.root = urljoin(endpoint, 'stac')
        self._encode_self()
        self._encode_parent()
        self._encode_children()
        self._encode_collection()
        self._encode_links()


    def _encode_parent(self):
        # ASSUMPTION: All collections belong to the root catalog
        self.parent = self.root if self.type == 'collection' else urljoin(self.endpoint, f'collections/{self.asset._data["collection"]}')

    def _encode_self(self):
        self.self = urljoin(self.endpoint, f'collections/{self.asset.id}') if self.type == 'collection' \
            else urljoin(self.endpoint, f'collections/{self.asset._data["collection"]}/items/{self.asset.id}')

    def _encode_children(self):
        # ASSUMPTION: only collections will have children
        self.items = urljoin(self.endpoint, f'collections/{self.asset.id}/items') if self.type == 'collection' else None

    def _encode_collection(self):
        # ASSUMPTION: Only items will have collections
        # ASSUMPTION: Item's parent and collection are the same
        self.collection = self.parent if self.type == 'item' else None

    def _encode_links(self):
        links = ['parent', 'self', 'items', 'root', 'collection']
        self.links = [{'rel': x, 'href': getattr(self, x)} for x in links if getattr(self, x)]



class AssetLoader(object):

    def __init__(self, asset, endpoint):
        self.asset = asset
        self.endpoint = endpoint
        self.type = 'item' if type(asset) is Item else 'collection' if type(asset) is Collection else None
        self.asset._data['links'] = LinkEncoder(self.asset, self.type, self.endpoint).links

    def ingest(self):
        # Ingest asset (either item or collection) into ArangoDB via foxx service
        # This should be a simple passthrough
        pass

class ArangoLoader(object):

    def __init__(self):
        self.config = ConfigLoader

    def ingest_collections(self, url):
        # TODO: recursive vs non-recursive ingest
        root = Collection.open(url)
        for coll in root.collections():
            AssetLoader(coll, self.config.API_ENDPOINT).ingest()

    def ingest_items(self, url):
        # TODO: recursive vs non-recursive ingest
        root = Collection.open(url)
        for item in root.items():
            AssetLoader(item, self.config.API_ENDPOINT).ingest()