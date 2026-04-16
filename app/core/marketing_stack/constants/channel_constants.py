class Channel:
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    GOOGLE_BUSINESS = "google_business"
    EMAIL = "email"
    SMS = "sms"
    YOUTUBE = "youtube"
    SEO = "seo"


class ContentType:
    POST = "post"
    REEL_SCRIPT = "reel_script"
    STORY = "story"
    CAROUSEL = "carousel"
    CAMPAIGN_MESSAGE = "campaign_message"
    AD_COPY = "ad_copy"
    BLOG = "blog"
    GMB_POST = "gmb_post"
    REVIEW_RESPONSE = "review_response"
    EMAIL_CAMPAIGN = "email_campaign"


class CampaignType:
    ORGANIC_POST = "organic_post"
    WHATSAPP_BROADCAST = "whatsapp_broadcast"
    PAID_AD = "paid_ad"
    EMAIL_CAMPAIGN = "email_campaign"


ALL_CHANNELS = [
    Channel.INSTAGRAM,
    Channel.WHATSAPP,
    Channel.FACEBOOK,
    Channel.GOOGLE_ADS,
    Channel.META_ADS,
    Channel.GOOGLE_BUSINESS,
    Channel.EMAIL,
    Channel.SMS,
    Channel.YOUTUBE,
    Channel.SEO,
]

MVP_CHANNELS = [
    Channel.INSTAGRAM,
    Channel.WHATSAPP,
]
