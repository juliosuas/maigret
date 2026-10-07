"""TikTok profile check (#3167).

Missing TikTok profiles are HTTP 200. The old absence marker
``serverCode":404`` is not in that response, so the check relied only on
the generic ``"nickname":`` key.
"""

from unittest.mock import Mock

from maigret.checking import process_site_result
from maigret.result import MaigretCheckStatus


def _check(site, username, body):
    info = {
        "username": username,
        "parsing_enabled": False,
        "url_user": f"https://www.tiktok.com/@{username}",
    }
    return process_site_result((body, 200, None), Mock(), Mock(), info, site)


def test_tiktok_real_profile_is_claimed(default_db):
    site = default_db.sites_dict["TikTok"]
    body = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">'
        '{"webapp.user-detail":{"userInfo":{"user":{"id":"1","uniqueId":"red",'
        '"nickname":"(RED)"}},"statusCode":0}}'
        "</script>"
    )
    out = _check(site, "red", body)
    assert out["status"].status == MaigretCheckStatus.CLAIMED


def test_tiktok_missing_profile_is_not_claimed_even_with_nickname(default_db):
    """#3167: not-found HTML is HTTP 200 and may still contain "nickname"."""
    site = default_db.sites_dict["TikTok"]
    body = (
        '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">'
        '{"webapp.user-detail":{"statusCode":10221,"statusMsg":""},'
        '"nickname":"suggested","uniqueId":"suggested"}'
        "</script>"
    )
    out = _check(site, "noonewouldeverusethis1", body)
    assert out["status"].status == MaigretCheckStatus.AVAILABLE


def test_tiktok_nickname_without_profile_id_is_not_claimed(default_db):
    """A shell that only mentions nickname must not count as a profile."""
    site = default_db.sites_dict["TikTok"]
    body = '<html>"nickname":"Set nickname?"</html>'
    out = _check(site, "xqz9k2m7w4p8n3", body)
    assert out["status"].status == MaigretCheckStatus.AVAILABLE
