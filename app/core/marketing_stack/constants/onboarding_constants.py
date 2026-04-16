ONBOARDING_QUESTIONS = [
    {
        "id": "q1_business_info",
        "question": "What's your business name and where is it located?",
        "example": "Example: Brew Culture, Jubilee Hills, Hyderabad",
    },
    {
        "id": "q2_services",
        "question": "What does your business do? What products or services do you offer?",
        "example": "Example: We serve specialty coffee, cold brews, sandwiches and pastries",
    },
    {
        "id": "q3_customers",
        "question": "Who are your typical customers?",
        "example": "Example: College students, IT professionals, couples",
    },
    {
        "id": "q4_pricing",
        "question": "What's your price range?",
        "example": "Example: Rs 150-400 per person",
    },
    {
        "id": "q5_usp",
        "question": "What makes your business different from competitors?",
        "example": "Example: We roast our own beans, pet-friendly, open till 1 AM",
    },
    {
        "id": "q6_photos",
        "question": "Send me 2-3 photos of your business (shop, products, team)",
        "example": "Just send the photos here in this chat",
    },
]

TOTAL_QUESTIONS = len(ONBOARDING_QUESTIONS)

ONBOARDING_WELCOME = (
    "Welcome! I'm your AI marketing assistant.\n\n"
    "I'll help you get more customers with zero effort from your side.\n\n"
    "Let's start — I need to understand your business. "
    "I'll ask you {total} quick questions.\n\n"
    "Or if you have a website, just send me the link and I'll figure out the rest!"
)

ONBOARDING_COMPLETE = (
    "Got it! I now understand your business.\n\n"
    "Give me 30 seconds to create your complete marketing plan..."
)
