"""
90-Day Launch Plan Templates
Week-by-week task structures for different brand types
"""

from typing import List, Dict

# SaaS Brand Launch Plan (13 weeks)
LAUNCH_PLAN_SAAS = [
    # PHASE 1: FOUNDATIONS (Weeks 1-4)
    {
        "week": 1,
        "phase": "Foundations",
        "deliverables": "Finalize Vision, Mission & Values; Define target customer persona; Document core problem and solution",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 2,
        "phase": "Foundations",
        "deliverables": "Complete competitive analysis; Define positioning statement; Outline key differentiators",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 3,
        "phase": "Foundations",
        "deliverables": "Create brand messaging guide; Define brand voice and tone; Draft key messaging pillars",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 4,
        "phase": "Foundations",
        "deliverables": "Design visual identity; Select color palette and typography; Create logo concepts",
        "owner": "Design",
        "status": "Pending"
    },
    
    # PHASE 2: DIGITAL PRESENCE (Weeks 5-8)
    {
        "week": 5,
        "phase": "Digital Presence",
        "deliverables": "Set up domain and hosting; Create website wireframes; Plan site structure and navigation",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 6,
        "phase": "Digital Presence",
        "deliverables": "Build landing page with clear value prop; Add email signup form; Implement analytics tracking",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 7,
        "phase": "Digital Presence",
        "deliverables": "Set up social media profiles; Create content calendar; Design social media templates",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 8,
        "phase": "Digital Presence",
        "deliverables": "Create lead magnet or demo; Build email nurture sequence; Set up CRM system",
        "owner": "Marketing",
        "status": "Pending"
    },
    
    # PHASE 3: LAUNCH & GROWTH (Weeks 9-13)
    {
        "week": 9,
        "phase": "Launch Prep",
        "deliverables": "Finalize launch messaging; Create press kit; Build launch day assets and content",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 10,
        "phase": "Launch Prep",
        "deliverables": "Set up Product Hunt profile; Prepare launch sequence; Brief beta users and advocates",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 11,
        "phase": "Launch",
        "deliverables": "Execute launch day plan; Monitor social mentions; Engage with early users",
        "owner": "All",
        "status": "Pending"
    },
    {
        "week": 12,
        "phase": "Growth",
        "deliverables": "Analyze launch metrics; Implement user feedback; Optimize conversion funnel",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 13,
        "phase": "Growth",
        "deliverables": "Scale successful channels; Begin content marketing; Plan next 90 days",
        "owner": "All",
        "status": "Pending"
    }
]

# D2C (Direct-to-Consumer) Brand Launch Plan
LAUNCH_PLAN_D2C = [
    # PHASE 1: FOUNDATIONS (Weeks 1-4)
    {
        "week": 1,
        "phase": "Foundations",
        "deliverables": "Define brand DNA and customer avatar; Research market and competitors; Validate product-market fit",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 2,
        "phase": "Foundations",
        "deliverables": "Finalize product line and pricing; Source suppliers and materials; Create brand story and narrative",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 3,
        "phase": "Foundations",
        "deliverables": "Develop visual brand identity; Create packaging design; Plan product photography",
        "owner": "Design",
        "status": "Pending"
    },
    {
        "week": 4,
        "phase": "Foundations",
        "deliverables": "Conduct product photoshoot; Create brand assets library; Finalize brand guidelines",
        "owner": "Design",
        "status": "Pending"
    },
    
    # PHASE 2: DIGITAL STOREFRONT (Weeks 5-8)
    {
        "week": 5,
        "phase": "E-commerce Setup",
        "deliverables": "Set up Shopify/e-commerce platform; Configure payment processing; Set up shipping and fulfillment",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 6,
        "phase": "E-commerce Setup",
        "deliverables": "Build store pages and product listings; Write compelling product descriptions; Optimize for mobile",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 7,
        "phase": "E-commerce Setup",
        "deliverables": "Set up email marketing platform; Create abandoned cart flows; Build welcome series",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 8,
        "phase": "E-commerce Setup",
        "deliverables": "Establish social media presence; Plan influencer partnerships; Create UGC strategy",
        "owner": "Marketing",
        "status": "Pending"
    },
    
    # PHASE 3: LAUNCH & SCALE (Weeks 9-13)
    {
        "week": 9,
        "phase": "Pre-Launch",
        "deliverables": "Build launch waitlist; Create pre-launch content; Engage early supporters",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 10,
        "phase": "Pre-Launch",
        "deliverables": "Set up Facebook/Instagram ads; Create launch promo offers; Prepare launch day content",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 11,
        "phase": "Launch",
        "deliverables": "Execute launch campaign; Go live on social media; Process first orders",
        "owner": "All",
        "status": "Pending"
    },
    {
        "week": 12,
        "phase": "Growth",
        "deliverables": "Analyze sales data and customer feedback; Optimize ads and landing pages; Scale winning campaigns",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 13,
        "phase": "Growth",
        "deliverables": "Expand to new channels; Build customer loyalty program; Plan next product launch",
        "owner": "All",
        "status": "Pending"
    }
]

# Agency/Service Brand Launch Plan
LAUNCH_PLAN_AGENCY = [
    {
        "week": 1,
        "phase": "Foundations",
        "deliverables": "Define service offerings and pricing; Identify ideal client profile; Document unique methodology",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 2,
        "phase": "Foundations",
        "deliverables": "Create brand positioning and messaging; Develop case study framework; Define service packages",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 3,
        "phase": "Foundations",
        "deliverables": "Design brand identity and templates; Create proposal template; Build client onboarding process",
        "owner": "Design",
        "status": "Pending"
    },
    {
        "week": 4,
        "phase": "Foundations",
        "deliverables": "Develop thought leadership content; Plan content strategy; Create lead magnets",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 5,
        "phase": "Digital Presence",
        "deliverables": "Build portfolio website; Showcase past work and results; Add service pages and CTAs",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 6,
        "phase": "Digital Presence",
        "deliverables": "Optimize LinkedIn profiles; Begin publishing thought leadership; Join relevant communities",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 7,
        "phase": "Digital Presence",
        "deliverables": "Launch email newsletter; Create referral program; Set up testimonial collection",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 8,
        "phase": "Digital Presence",
        "deliverables": "Guest post on industry blogs; Speak at local events; Build authority and credibility",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 9,
        "phase": "Client Acquisition",
        "deliverables": "Launch outbound prospecting; Create cold email sequences; Begin networking actively",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 10,
        "phase": "Client Acquisition",
        "deliverables": "Attend industry conferences; Pitch to warm leads; Run pilot projects",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 11,
        "phase": "Launch",
        "deliverables": "Announce official launch; Share client wins; Publish comprehensive case studies",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 12,
        "phase": "Growth",
        "deliverables": "Optimize sales process; Implement CRM; Track key metrics",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 13,
        "phase": "Growth",
        "deliverables": "Scale what's working; Build strategic partnerships; Plan team expansion",
        "owner": "Founder",
        "status": "Pending"
    }
]

# E-commerce Marketplace Brand
LAUNCH_PLAN_ECOMMERCE = [
    {
        "week": 1,
        "phase": "Foundations",
        "deliverables": "Define product categories and niche; Research suppliers and vendors; Validate market demand",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 2,
        "phase": "Foundations",
        "deliverables": "Finalize brand name and positioning; Create brand story; Design visual identity",
        "owner": "Founder",
        "status": "Pending"
    },
    {
        "week": 3,
        "phase": "Product Sourcing",
        "deliverables": "Source initial product inventory; Negotiate terms with suppliers; Order samples for testing",
        "owner": "Operations",
        "status": "Pending"
    },
    {
        "week": 4,
        "phase": "Product Sourcing",
        "deliverables": "Conduct product photography; Write SEO-optimized descriptions; Set pricing strategy",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 5,
        "phase": "Platform Setup",
        "deliverables": "Build e-commerce website; Configure payment gateway; Set up inventory management",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 6,
        "phase": "Platform Setup",
        "deliverables": "Upload products to site; Create collection pages; Optimize site for conversions",
        "owner": "Tech",
        "status": "Pending"
    },
    {
        "week": 7,
        "phase": "Marketing Setup",
        "deliverables": "Set up Google Analytics and tracking; Create Facebook/Instagram business accounts; Plan content calendar",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 8,
        "phase": "Marketing Setup",
        "deliverables": "Build email list with lead magnet; Create automated email flows; Set up customer support system",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 9,
        "phase": "Pre-Launch",
        "deliverables": "Test checkout process; Run soft launch with friends/family; Gather initial feedback",
        "owner": "All",
        "status": "Pending"
    },
    {
        "week": 10,
        "phase": "Pre-Launch",
        "deliverables": "Create launch promotion; Set up paid ads campaigns; Build influencer partnerships",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 11,
        "phase": "Launch",
        "deliverables": "Official launch announcement; Activate paid marketing; Monitor and fulfill orders",
        "owner": "All",
        "status": "Pending"
    },
    {
        "week": 12,
        "phase": "Optimization",
        "deliverables": "Analyze sales data; Optimize ad performance; Improve product pages based on data",
        "owner": "Marketing",
        "status": "Pending"
    },
    {
        "week": 13,
        "phase": "Scale",
        "deliverables": "Expand product catalog; Scale winning ad campaigns; Plan Q2 strategy",
        "owner": "All",
        "status": "Pending"
    }
]


def get_launch_plan_template(brand_type: str) -> List[Dict]:
    """
    Get the appropriate launch plan template based on brand type.
    
    Args:
        brand_type: One of 'SaaS', 'D2C', 'Agency', 'E-commerce'
        
    Returns:
        List of week dictionaries
    """
    templates = {
        "SaaS": LAUNCH_PLAN_SAAS,
        "D2C": LAUNCH_PLAN_D2C,
        "Agency": LAUNCH_PLAN_AGENCY,
        "E-commerce": LAUNCH_PLAN_ECOMMERCE
    }
    
    return templates.get(brand_type, LAUNCH_PLAN_SAAS)


def get_available_brand_types() -> List[str]:
    """Return list of supported brand types."""
    return ["SaaS", "D2C", "Agency", "E-commerce"]
