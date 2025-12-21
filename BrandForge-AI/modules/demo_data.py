"""
Demo Mode - Sample Data for BrandForge AI
Provides pre-filled examples for quick demos and testing
"""

from modules.state import BrandState
from typing import Dict


def get_demo_company(demo_type: str = "saas") -> Dict:
    """
    Get pre-filled demo company data.
    
    Args:
        demo_type: Type of demo ("saas", "d2c", "agency", "ecommerce")
        
    Returns:
        Dictionary with complete brand state
    """
    
    demos = {
        "saas": {
            "company_name": "FlowSync AI",
            "target_audience": "Tech-savvy professionals aged 25-45 at mid-size companies seeking workflow automation",
            "core_problem": "Teams waste 40% of their time on repetitive tasks and manual data entry across disconnected tools",
            "brand_voice": "Professional",
            "brand_type": "SaaS",
            
            # Pre-generated foundations
            "vision": "To create a world where every professional can focus on meaningful work, freed from the burden of repetitive tasks",
            "mission": "FlowSync AI empowers teams to automate their workflows with intelligent, no-code solutions that integrate seamlessly with existing tools",
            "values": [
                "Innovation: Continuously pushing boundaries of automation technology",
                "Simplicity: Making powerful tools accessible to everyone",
                "Reliability: Building systems teams can depend on 24/7",
                "Transparency: Clear pricing, honest communication, open roadmap",
                "Impact: Measuring success by hours saved and teams empowered"
            ],
            
            "positioning_statement": "For tech-savvy professionals who struggle with repetitive workflows, FlowSync AI is the intelligent automation platform that eliminates manual tasks without requiring coding expertise, unlike traditional RPA tools that demand technical skills and lengthy implementation",
            
            # Identity elements
            "color_palette_desc": "Primary: Deep Ocean Blue (#0047AB) - trust, professionalism, technology. Secondary: Electric Teal (#00CED1) - innovation, energy, digital transformation. Accent: Warm Gold (#FFB700) - value, success, achievement. Neutrals: Charcoal (#2C3E50), Light Gray (#ECF0F1), Pure White (#FFFFFF)",
            
            "font_recommendations": "Headers: Inter Bold - modern, readable, tech-forward. Body: Inter Regular - clean, professional, excellent web readability. Code/Technical: Fira Code - monospaced, developer-friendly. Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI'",
            
            "messaging_guide": """**Brand Voice:** Professional yet approachable, technically credible without jargon

**Tone Variations:**
- Website/Marketing: Confident, solution-oriented, aspirational
- Product/UI: Clear, helpful, action-oriented
- Support: Empathetic, patient, solution-focused
- Social Media: Friendly, insightful, community-driven

**Key Messages:**
1. "Automate anything in minutes, not months"
2. "No code required, unlimited possibilities"
3. "Your team's AI-powered productivity partner"

**Do's:**
- Use active voice and strong verbs
- Lead with benefits, support with features
- Show, don't just tell (use examples)
- Acknowledge challenges before presenting solutions

**Don'ts:**
- Avoid buzzwords without context
- Never oversimplify complex problems
- Don't make promises we can't keep
- Avoid technical jargon in marketing""",
            
            "tagline": "Automate Work. Amplify Impact.",
            "value_proposition": "FlowSync AI eliminates 40% of repetitive work through intelligent automation that requires zero coding, saving teams an average of 15 hours per week",
            "elevator_pitch": "FlowSync AI is an intelligent automation platform that helps teams eliminate repetitive tasks without writing code. Unlike traditional tools that require technical expertise, our AI-powered system learns your workflows and automates them in minutes. We're already helping over 2,000 teams save 15+ hours per week.",
            
            # KPI parameters
            "initial_audience_size": 2000,
            "weekly_growth_rate": 0.20,
            "conversion_rate": 0.08,
            "avg_customer_value": 150
        },
        
        "d2c": {
            "company_name": "EcoBloom Organics",
            "target_audience": "Health-conscious millennials aged 25-40 who prioritize sustainability and natural wellness",
            "core_problem": "Consumers struggle to find truly organic, sustainably-sourced wellness products they can trust",
            "brand_voice": "Friendly",
            "brand_type": "D2C",
            
            "vision": "To cultivate a healthier planet where natural wellness is accessible to everyone",
            "mission": "EcoBloom Organics delivers farm-fresh, certified organic wellness products directly to your door, supporting regenerative agriculture and transparent supply chains",
            "values": [
                "Purity: 100% organic, nothing artificial ever",
                "Sustainability: Carbon-neutral from farm to doorstep",
                "Transparency: Know your farmer, trace your product",
                "Community: Supporting local farmers and global wellness",
                "Authenticity: Real ingredients, real results, real impact"
            ],
            
            "positioning_statement": "For health-conscious consumers who don't want to compromise, EcoBloom Organics is the wellness brand that delivers certified organic products with full farm-to-door traceability, unlike mass-market brands that obscure their supply chains",
            
            "color_palette_desc": "Primary: Forest Green (#2D5016) - nature, growth, organic. Secondary: Soft Cream (#FFF8DC) - purity, natural, gentle. Accent: Terracotta (#E07856) - earthiness, warmth, vitality. Neutrals: Sage (#9CAF88), Warm White (#FAF9F6)",
            
            "font_recommendations": "Headers: Playfair Display - elegant, natural, premium. Body: Lato - clean, readable, approachable. Accent: Pacifico - handcrafted, personal touch.",
            
            "messaging_guide": """**Brand Voice:** Warm, authentic, knowledge-sharing

**Tone:** Like chatting with a knowledgeable friend who genuinely cares about your wellness journey

**Key Messages:**
1. "From our family farms to your family table"
2. "Organic certified, carbon neutral, completely transparent"
3. "Wellness that nourishes you and the planet"

**Style:**
- Storytelling over selling
- Education over persuasion  
- Community over competition""",
            
            "tagline": "Pure Wellness, Naturally Delivered",
            "value_proposition": "Certified organic wellness products sourced directly from regenerative farms, with full supply chain transparency and carbon-neutral delivery",
            
            "initial_audience_size": 1500,
            "weekly_growth_rate": 0.18,
            "conversion_rate": 0.12,
            "avg_customer_value": 85
        },
        
        "agency": {
            "company_name": "Quantum Creative Studio",
            "target_audience": "Fast-growing startups and scale-ups that need strategic brand work, not just pretty designs",
            "core_problem": "Growing companies struggle to find creative partners who understand business strategy and move at startup speed",
            "brand_voice": "Bold",
            "brand_type": "Agency",
            
            "vision": "To redefine how brands are built in the age of rapid digital transformation",
            "mission": "Quantum Creative Studio partners with ambitious companies to build brands that don't just look good—they drive growth, build trust, and stand out in crowded markets",
            "values": [
                "Strategic Thinking: Design with business impact in mind",
                "Velocity: Move at the speed of your ambition",
                "Collaboration: Your success is our success",
                "Craft: Sweat the details, perfect the execution",
                "Results: Beautiful work that delivers measurable outcomes"
            ],
            
            "positioning_statement": "For fast-growing companies that need more than a design shop, Quantum Creative Studio is the strategic branding partner that combines creative excellence with business acumen to drive measurable growth",
            
            "color_palette_desc": "Primary: Quantum Black (#0A0A0A) - sophistication, power, clarity. Secondary: Electric Violet (#8B00FF) - creativity, innovation, energy. Accent: Neon Cyan (#00FFFF) - digital, modern, attention-grabbing. Neutrals: Slate (#4A5568), Soft White (#F7FAFC)",
            
            "font_recommendations": "Headers: Bebas Neue - bold, impactful, confident. Body: Work Sans - modern, clean, professional. Accent: Space Mono - technical, unique, memorable.",
            
            "messaging_guide": """**Brand Voice:** Confident, strategic, results-driven

**Tone:** Like a seasoned strategist who's been in the trenches and knows what actually works

**Key Messages:**
1. "Brands built for growth, not just for show"
2. "Strategy first, aesthetics always"
3. "Your ambitious partner for what's next"

**Style:**
- Direct and confident
- Data-informed storytelling
- Case studies over claims
- Challenge conventional thinking""",
            
            "tagline": "Build Brands That Mean Business",
            "value_proposition": "Strategic brand development that combines creative excellence with data-driven business strategy, delivering measurable growth for ambitious companies",
            
            "initial_audience_size": 800,
            "weekly_growth_rate": 0.15,
            "conversion_rate": 0.25,
            "avg_customer_value": 5000
        }
    }
    
    return demos.get(demo_type.lower(), demos["saas"])


def load_demo_state(demo_type: str = "saas") -> Dict:
    """
    Load a complete demo state with all workflow steps completed.
    
    Args:
        demo_type: Type of demo to load
        
    Returns:
        Complete BrandState dictionary
    """
    from modules.state import create_empty_state
    
    demo_data = get_demo_company(demo_type)
    state = create_empty_state()
    
    # Copy all demo data into state
    for key, value in demo_data.items():
        state[key] = value
    
    # Mark workflow steps as completed
    state["current_step"] = 5  # All steps complete
    
    # Add sample launch plan
    state["launch_plan_df"] = [
        {"week": 1, "phase": "Foundation", "task": "Brand strategy finalized", "owner": "Founder", "status": "Planning"},
        {"week": 2, "phase": "Foundation", "task": "Website wireframes completed", "owner": "Design Team", "status": "Planning"},
        {"week": 3, "phase": "Foundation", "task": "Core product features defined", "owner": "Product Team", "status": "Planning"},
        {"week": 4, "phase": "Build", "task": "MVP development started", "owner": "Engineering", "status": "Planning"},
        {"week": 5, "phase": "Build", "task": "Brand identity assets created", "owner": "Design Team", "status": "Planning"},
        {"week": 6, "phase": "Build", "task": "Website development", "owner": "Dev Team", "status": "Planning"},
        {"week": 7, "phase": "Build", "task": "Content creation for launch", "owner": "Marketing", "status": "Planning"},
        {"week": 8, "phase": "Pre-Launch", "task": "Beta user recruitment", "owner": "Community Lead", "status": "Planning"},
        {"week": 9, "phase": "Pre-Launch", "task": "Press kit preparation", "owner": "Marketing", "status": "Planning"},
        {"week": 10, "phase": "Launch", "task": "Official product launch", "owner": "Founder", "status": "Planning"},
        {"week": 11, "phase": "Launch", "task": "Launch marketing campaign", "owner": "Marketing", "status": "Planning"},
        {"week": 12, "phase": "Growth", "task": "User feedback collection", "owner": "Product Team", "status": "Planning"},
        {"week": 13, "phase": "Growth", "task": "Growth optimization begins", "owner": "Growth Team", "status": "Planning"}
    ]
    
    # Add sample KPI projections
    state["kpi_projections"] = []
    base_visitors = state.get("initial_audience_size", 1000)
    growth = state.get("weekly_growth_rate", 0.15)
    conversion = state.get("conversion_rate", 0.05)
    value = state.get("avg_customer_value", 100)
    
    for week in range(1, 14):
        visitors = int(base_visitors * ((1 + growth) ** week))
        conversions = int(visitors * conversion)
        revenue = conversions * value
        
        state["kpi_projections"].append({
            "Week": week,
            "Visitors": visitors,
            "Signups": conversions,
            "Leads": int(conversions * 0.5),
            "Revenue": revenue,
            "Conversion_Rate": f"{conversion * 100:.1f}%"
        })
    
    return state


# Available demo types
DEMO_TYPES = {
    "saas": "🚀 SaaS Startup (FlowSync AI)",
    "d2c": "🌱 D2C Brand (EcoBloom Organics)",
    "agency": "⚡ Creative Agency (Quantum Creative)"
}


def get_demo_names() -> Dict[str, str]:
    """Get mapping of demo types to display names."""
    return DEMO_TYPES
