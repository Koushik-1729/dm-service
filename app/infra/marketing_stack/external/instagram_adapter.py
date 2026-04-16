from typing import List, Dict, Any, Optional
import asyncio
from loguru import logger
import httpx

from app.core.marketing_stack.outbound.external.social_media_port import SocialMediaPort
from app.common.constants import INSTAGRAM_API_BASE
from app.monitoring.metrics import CONTENT_GENERATED


class InstagramAdapter(SocialMediaPort):
    """Meta Instagram Graph API adapter implementing SocialMediaPort.

    Publishing flow (Container-based):
    1. Create a media container (POST /{ig-user-id}/media)
    2. Wait for container to be ready
    3. Publish the container (POST /{ig-user-id}/media_publish)
    """

    def __init__(self, business_account_id: str, access_token: str):
        self._account_id = business_account_id
        self._access_token = access_token
        self._base_url = f"{INSTAGRAM_API_BASE}/{business_account_id}"
        self._headers = {"Authorization": f"Bearer {access_token}"}

    async def publish_post(self, image_url: str, caption: str) -> str:
        if not image_url:
            logger.warning("No image URL provided for Instagram post, skipping publish")
            raise ValueError("image_url is required for Instagram posts")

        # Step 1: Create media container
        container_id = await self._create_container(image_url=image_url, caption=caption)

        # Step 2: Wait for processing
        await self._wait_for_container(container_id)

        # Step 3: Publish
        post_id = await self._publish_container(container_id)

        CONTENT_GENERATED.labels(channel="instagram", content_type="post").inc()
        logger.info(f"Instagram post published: {post_id}")
        return post_id

    async def publish_carousel(self, image_urls: List[str], caption: str) -> str:
        if len(image_urls) < 2:
            raise ValueError("Carousel requires at least 2 images")

        # Step 1: Create individual item containers
        item_ids = []
        for url in image_urls[:10]:  # Max 10 items
            container_id = await self._create_container(image_url=url, is_carousel_item=True)
            item_ids.append(container_id)

        # Step 2: Create carousel container
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/media",
                params={
                    "media_type": "CAROUSEL",
                    "caption": caption,
                    "children": ",".join(item_ids),
                    "access_token": self._access_token,
                },
            )
            response.raise_for_status()
            carousel_container_id = response.json()["id"]

        # Step 3: Wait and publish
        await self._wait_for_container(carousel_container_id)
        post_id = await self._publish_container(carousel_container_id)

        CONTENT_GENERATED.labels(channel="instagram", content_type="carousel").inc()
        logger.info(f"Instagram carousel published: {post_id}")
        return post_id

    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{INSTAGRAM_API_BASE}/{post_id}/insights",
                params={
                    "metric": "impressions,reach,engagement,saved",
                    "access_token": self._access_token,
                },
            )

            if response.status_code != 200:
                logger.warning(f"Failed to get post insights for {post_id}: {response.text[:200]}")
                return {}

            data = response.json()
            insights = {}
            for item in data.get("data", []):
                insights[item["name"]] = item["values"][0]["value"] if item.get("values") else 0
            return insights

    async def get_account_insights(
        self,
        period: str = "day",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if metrics is None:
            metrics = ["impressions", "reach", "follower_count"]

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self._base_url}/insights",
                params={
                    "metric": ",".join(metrics),
                    "period": period,
                    "access_token": self._access_token,
                },
            )

            if response.status_code != 200:
                logger.warning(f"Failed to get account insights: {response.text[:200]}")
                return {}

            data = response.json()
            insights = {}
            for item in data.get("data", []):
                values = item.get("values", [])
                insights[item["name"]] = values[-1]["value"] if values else 0
            return insights

    async def _create_container(
        self,
        image_url: str,
        caption: str = "",
        is_carousel_item: bool = False,
    ) -> str:
        params = {
            "image_url": image_url,
            "access_token": self._access_token,
        }
        if is_carousel_item:
            params["is_carousel_item"] = "true"
        else:
            params["caption"] = caption

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self._base_url}/media", params=params)
            if response.status_code not in (200, 201):
                logger.error(f"Instagram container creation failed: {response.text[:300]}")
                response.raise_for_status()
            return response.json()["id"]

    async def _wait_for_container(self, container_id: str, max_attempts: int = 10) -> None:
        for attempt in range(max_attempts):
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{INSTAGRAM_API_BASE}/{container_id}",
                    params={"fields": "status_code", "access_token": self._access_token},
                )
                status = response.json().get("status_code")

                if status == "FINISHED":
                    return
                if status == "ERROR":
                    error = response.json().get("status", "Unknown error")
                    raise RuntimeError(f"Instagram container processing failed: {error}")

            await asyncio.sleep(2)

        raise TimeoutError(f"Instagram container {container_id} did not finish processing")

    async def _publish_container(self, container_id: str) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self._access_token,
                },
            )
            if response.status_code not in (200, 201):
                logger.error(f"Instagram publish failed: {response.text[:300]}")
                response.raise_for_status()
            return response.json()["id"]
