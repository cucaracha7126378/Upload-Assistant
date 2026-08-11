# Upload Assistant © 2025 Audionut & wastaken7 — Licensed under UAPL v1.0
from typing import Any, Optional, cast

from src.rehostimages import RehostImagesManager
from src.trackers.COMMON import COMMON
from src.trackers.UNIT3D import UNIT3D

CAT_DOCU = '12'

Meta = dict[str, Any]
Config = dict[str, Any]


class THR(UNIT3D):
    def __init__(self, config: Config) -> None:
        super().__init__(config, tracker_name='THR')
        self.config = config
        self.common = COMMON(config)
        self.rehost_images_manager = RehostImagesManager(config)
        self.tracker = 'THR'
        self.base_url = 'https://www.torrenthr.org'
        self.id_url = f'{self.base_url}/api/torrents/'
        self.upload_url = f'{self.base_url}/api/torrents/upload'
        self.search_url = f'{self.base_url}/api/torrents/filter'
        self.torrent_url = f'{self.base_url}/torrents/'
        self.approved_image_hosts = ['thrimg']
        self.banned_groups = []
        pass

    # TODO crtići? 'animation' in genres ?
    async def get_category_id(
        self,
        meta: Meta,
        category: Optional[str] = None,
        reverse: bool = False,
        mapping_only: bool = False,
    ) -> dict[str, str]:
        _ = (category, reverse, mapping_only)
        genres = str(meta.get('genres', '')).lower()
        keywords = str(meta.get('keywords', '')).lower()
        category = str(meta.get('category', ''))
        is_disc = str(meta.get('is_disc', ''))
        sd = int(meta.get('sd', 0) or 0)
        cat = '17'

        if 'documentary' in genres or 'documentary' in keywords:
            cat = CAT_DOCU
        elif category == "MOVIE":
            if is_disc == "BMDV":
                cat = '40'
            elif is_disc in {"DVD", "HDDVD"}:
                cat = '14'
            else:
                cat = '4' if sd == 1 else '17'
        elif category == "TV":
            cat = '7' if sd == 1 else '34'
        elif bool(meta.get('anime')):
            cat = '31'
        return {'category_id': cat}

    async def get_type_id(
        self,
        meta: Meta,
        type: Optional[str] = None,
        reverse: bool = False,
        mapping_only: bool = False
    ) -> dict[str, str]:
        _ = (type, reverse, mapping_only)
        type_value = str(meta.get('type', ''))
        type_id = {
            'DISC': '1',
            'REMUX': '2',
            'WEBDL': '4',
            'WEBRIP': '5',
            'HDTV': '6',
            'ENCODE': '3',
            'DVDRIP': '3',
            'CAM': '7',
        }.get(type_value, '0')
        return {'type_id': type_id}

    async def check_image_hosts(self, meta: Meta) -> None:
        url_host_mapping = {
            "img.torrenthr.org": "thrimg",
            "img2.torrenthr.org": "thrimg",
            "slike.torrenthr.org": "thrimg",
        }

        await self.rehost_images_manager.check_hosts(
            meta,
            self.tracker,
            url_host_mapping=url_host_mapping,
            img_host_index=1,
            approved_image_hosts=self.approved_image_hosts,
        )
        return


    async def get_resolution_id(
        self,
        meta: Meta,
        resolution: Optional[str] = None,
        reverse: bool = False,
        mapping_only: bool = False,
    ) -> dict[str, str]:
        _ = (resolution, reverse, mapping_only)
        resolution_id = {
            # ID 10 nije "8640p" već "Ostalo"
            '4320p': '1',
            '2160p': '2',
            '1440p': '3',
            '1080p': '3',
            '1080i': '4',
            '720p': '5',
            '576p': '6',
            '576i': '7',
            '480p': '8',
            '480i': '9'
        }.get(meta['resolution'], '10')
        return {'resolution_id': resolution_id}

    async def get_additional_data(self, meta: Meta) -> dict[str, Any]:
        data: dict[str, Any] = {
            'mod_queue_opt_in': await self.get_flag(meta, 'modq'),
        }

        return data

    async def get_tvdb(self, meta: dict[str, Any]) -> dict[str, str]:
        cat_id = str((await self.get_category_id(meta))['category_id'])
        does_need_tvdb = meta["category"] == "TV" and cat_id not in [CAT_DOCU]
        tvdb = meta.get("tvdb_id", 0) if does_need_tvdb else 0
        return {"tvdb": f"{tvdb}"}

    async def get_season_number(self, meta: dict[str, Any]) -> dict[str, str]:
        data = {}
        cat_id = str((await self.get_category_id(meta))['category_id'])
        if meta.get("category") == "TV" and cat_id not in [CAT_DOCU]:
            data = {"season_number": f"{meta.get('season_int', '0')}"}

        return data

    async def get_episode_number(self, meta: dict[str, Any]) -> dict[str, str]:
        data = {}
        cat_id = str((await self.get_category_id(meta))['category_id'])
        if meta.get("category") == "TV" and cat_id not in [CAT_DOCU]:
            data = {"episode_number": f"{meta.get('episode_int', '0')}"}

        return data

