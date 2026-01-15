"""
Celery tasks for the automation app.
"""
import logging
from celery import shared_task
from django.utils import timezone

from .constants import TEST_ACCESS_TOKEN, TWITTER_TEST_ACCESS_TOKEN

logger = logging.getLogger(__name__)


@shared_task(name="automation.publish_scheduled_posts")
def publish_scheduled_posts():
    """
    Celery task to automatically publish scheduled posts that are due.
    This task should be run periodically (e.g., every minute) via Celery Beat.
    """
    from automation.models import ContentCalendar
    from automation.services import linkedin_service, twitter_service

    now = timezone.now()

    # Get all scheduled posts that are due (scheduled_date <= now)
    due_posts = ContentCalendar.objects.filter(
        status="scheduled", scheduled_date__lte=now
    )

    published_count = 0
    failed_count = 0

    for content in due_posts:
        logger.info(f"Auto-publishing scheduled post: {content.title}")

        results = {}
        errors = []

        # Publish to each connected platform
        for profile in content.social_profiles.all():
            if profile.platform == "linkedin" and profile.status == "connected":
                try:
                    # Check if test mode
                    if profile.access_token == TEST_ACCESS_TOKEN:
                        results["linkedin"] = {
                            "test_mode": True,
                            "message": "Post simulated in test mode",
                        }
                        logger.info(f"Test auto-publish to LinkedIn: {content.title}")
                    else:
                        access_token = profile.get_valid_access_token()
                        result = linkedin_service.create_share(
                            access_token=access_token,
                            user_urn=profile.profile_id,
                            text=content.content,
                        )
                        results["linkedin"] = result
                        logger.info(
                            f"Successfully published to LinkedIn: {content.title}"
                        )
                except Exception as e:
                    errors.append(f"LinkedIn: {str(e)}")
                    logger.error(f"Failed to auto-publish to LinkedIn: {e}")

            elif profile.platform == "twitter" and profile.status == "connected":
                try:
                    # Check if test mode
                    if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
                        results["twitter"] = {
                            "test_mode": True,
                            "message": "Tweet simulated in test mode",
                        }
                        logger.info(f"Test auto-publish to Twitter: {content.title}")
                    else:
                        access_token = profile.get_valid_access_token()
                        result = twitter_service.create_tweet(
                            access_token=access_token,
                            text=content.content,
                        )
                        results["twitter"] = result
                        logger.info(
                            f"Successfully published to Twitter: {content.title}"
                        )
                except Exception as e:
                    errors.append(f"Twitter: {str(e)}")
                    logger.error(f"Failed to auto-publish to Twitter: {e}")

        # Update content status
        if errors and not results:
            content.status = "failed"
            content.post_results = {"errors": errors}
            failed_count += 1
        else:
            content.status = "published"
            content.published_at = timezone.now()
            content.post_results = results
            published_count += 1

        content.save()

    logger.info(
        f"Auto-publish completed: {published_count} published, {failed_count} failed"
    )
    return {
        "published": published_count,
        "failed": failed_count,
        "timestamp": now.isoformat(),
    }


@shared_task(name="automation.publish_single_post")
def publish_single_post(content_id):
    """
    Celery task to publish a single scheduled post.
    This can be called when a post is scheduled to run at a specific time.
    """
    from automation.models import ContentCalendar
    from automation.services import linkedin_service, twitter_service

    try:
        content = ContentCalendar.objects.get(id=content_id)
    except ContentCalendar.DoesNotExist:
        logger.error(f"Content with id {content_id} not found")
        return {"error": "Content not found"}

    if content.status != "scheduled":
        logger.warning(
            f"Content {content_id} is not in scheduled status: {content.status}"
        )
        return {"error": f"Content is {content.status}, not scheduled"}

    logger.info(f"Publishing scheduled post: {content.title}")

    results = {}
    errors = []

    # Publish to each connected platform
    for profile in content.social_profiles.all():
        if profile.platform == "linkedin" and profile.status == "connected":
            try:
                # Check if test mode
                if profile.access_token == TEST_ACCESS_TOKEN:
                    results["linkedin"] = {
                        "test_mode": True,
                        "message": "Post simulated in test mode",
                    }
                    logger.info(f"Test publish to LinkedIn: {content.title}")
                else:
                    access_token = profile.get_valid_access_token()
                    result = linkedin_service.create_share(
                        access_token=access_token,
                        user_urn=profile.profile_id,
                        text=content.content,
                    )
                    results["linkedin"] = result
                    logger.info(f"Successfully published to LinkedIn: {content.title}")
            except Exception as e:
                errors.append(f"LinkedIn: {str(e)}")
                logger.error(f"Failed to publish to LinkedIn: {e}")

        elif profile.platform == "twitter" and profile.status == "connected":
            try:
                # Check if test mode
                if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
                    results["twitter"] = {
                        "test_mode": True,
                        "message": "Tweet simulated in test mode",
                    }
                    logger.info(f"Test publish to Twitter: {content.title}")
                else:
                    access_token = profile.get_valid_access_token()
                    result = twitter_service.create_tweet(
                        access_token=access_token,
                        text=content.content,
                    )
                    results["twitter"] = result
                    logger.info(f"Successfully published to Twitter: {content.title}")
            except Exception as e:
                errors.append(f"Twitter: {str(e)}")
                logger.error(f"Failed to publish to Twitter: {e}")

    # Update content status
    if errors and not results:
        content.status = "failed"
        content.post_results = {"errors": errors}
    else:
        content.status = "published"
        content.published_at = timezone.now()
        content.post_results = results

    content.save()

    return {
        "content_id": content_id,
        "status": content.status,
        "results": results,
        "errors": errors,
    }
