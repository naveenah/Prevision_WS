"""
AI Prompt Templates for BrandForge AI
Optimized for Google Gemini Pro 3 (gemini-2.0-flash-exp)
"""

# Foundation Builder Prompt
FOUNDATION_PROMPT = """You are an expert Brand Strategist with 15 years of experience helping founders build compelling brands.

**Company Information:**
- Company Name: {company_name}
- Target Audience: {target_audience}
- Core Problem Solved: {core_problem}
- Brand Voice: {brand_voice}

**Your Task:**
Generate a comprehensive brand foundation including:

1. **Vision Statement** (1-2 sentences)
   - Aspirational and future-focused
   - Describes the world you want to create
   - Inspirational and motivating

2. **Mission Statement** (1-2 sentences)
   - Action-oriented and present-focused
   - Clearly states what you do and for whom
   - Concrete and achievable

3. **Core Values** (Exactly 5 values)
   - Each value should be 1-3 words
   - Include a brief 1-sentence explanation for each
   - Should align with the brand voice and audience

**Output Format:**
Return ONLY a valid JSON object with this exact structure:
{{
  "vision": "Your vision statement here...",
  "mission": "Your mission statement here...",
  "values": [
    "Value 1: Brief explanation",
    "Value 2: Brief explanation",
    "Value 3: Brief explanation",
    "Value 4: Brief explanation",
    "Value 5: Brief explanation"
  ]
}}

**Important Guidelines:**
- Keep vision/mission statements concise (max 2 sentences each)
- Make it authentic and specific to THIS company
- Avoid generic corporate jargon
- Align tone with the specified brand voice
- Return ONLY the JSON, no additional text
"""

# Positioning Statement Prompt
POSITIONING_PROMPT = """You are a Brand Positioning Expert specializing in competitive differentiation.

**Brand Context:**
- Company: {company_name}
- Target Audience: {target_audience}
- Core Problem: {core_problem}
- Brand Voice: {brand_voice}
- Core Values: {values}

**Your Task:**
Create a powerful positioning statement that differentiates this brand in the market.

**Positioning Statement Format:**
"For [target audience] who [need/problem], [company name] is the [category] that [unique benefit]. Unlike [competitors/alternatives], we [key differentiator]."

**Requirements:**
- Make it specific and memorable
- Focus on unique value proposition
- Address the audience's pain point directly
- Highlight clear differentiation
- Keep it to 2-3 sentences maximum

Return ONLY the positioning statement text, no additional explanation.
"""

# Competitor Analysis Prompt
COMPETITOR_ANALYSIS_PROMPT = """You are a Market Research Analyst with expertise in competitive intelligence.

**Our Brand:**
- Company: {company_name}
- Positioning: {positioning_statement}
- Core Values: {values}
- Target Audience: {target_audience}

**Competitors:**
{competitors_list}

**Your Task:**
Conduct a comprehensive Gap Analysis identifying opportunities for differentiation.

**Analysis Structure:**

## Competitive Landscape Overview
Brief summary of the market and competitor strengths.

## Where Competitors Are Strong
List 3-4 areas where competitors dominate.

## Differentiation Opportunities
Identify 3-5 specific ways we can stand out:
- What unique angles can we take?
- What customer needs are underserved?
- What can we do better/differently?

## Recommended Positioning Strategy
Provide 2-3 specific strategic recommendations for how to compete effectively.

## Key Insights
3-5 bullet points of critical insights about the competitive landscape.

Return as well-formatted markdown with clear sections.
"""

# Brand Identity Generator Prompt
BRAND_IDENTITY_PROMPT = """You are a Brand Identity Designer with expertise in visual branding and color psychology.

**Brand Context:**
- Company: {company_name}
- Brand Voice: {brand_voice}
- Core Values: {values}
- Target Audience: {target_audience}
- Positioning: {positioning}

**Your Task:**
Design a comprehensive brand identity system.

**Generate:**

1. **Color Palette** (3-4 colors)
   - Primary color with psychological rationale
   - Secondary color(s) for support
   - Explain why each color fits the brand voice and audience
   - Include hex codes as suggestions

2. **Typography Recommendations**
   - Primary font (for headlines/brand)
   - Secondary font (for body text)
   - Rationale for each choice
   - Suggest specific font families or styles

3. **Brand Messaging Guide**
   - Tone of voice description (2-3 paragraphs)
   - Do's and Don'ts (at least 3 each)
   - Example phrases that fit the brand voice
   - Language style guidelines

**Output Format:**
Return as valid JSON:
{{
  "color_palette_desc": "Detailed description of colors with rationale...",
  "font_recommendations": "Font pairing recommendations with reasoning...",
  "messaging_guide": "Complete messaging guide in markdown format..."
}}

Return ONLY the JSON object, no additional text.
"""

# 90-Day Plan Customization Prompt
LAUNCH_PLAN_CUSTOMIZATION_PROMPT = """You are a Launch Strategy Consultant specializing in {brand_type} businesses.

**Brand Details:**
- Company: {company_name}
- Brand Type: {brand_type}
- Target Audience: {target_audience}
- Launch Date: {launch_date}

**Your Task:**
Enhance the standard 90-day launch plan with specific, actionable tasks tailored to this brand.

**For each phase, provide:**

**Phase 1: Foundations (Weeks 1-4)**
- Specific deliverables unique to this brand type
- Key stakeholders to involve
- Critical decisions to make

**Phase 2: Digital Presence (Weeks 5-8)**
- Platform-specific recommendations
- Content strategy aligned with audience
- Technical setup requirements

**Phase 3: Launch & Growth (Weeks 9-13)**
- Launch tactics specific to {brand_type}
- Growth channels to prioritize
- Metrics to track

**Output Format:**
For each week (1-13), provide:
- Week number
- Phase name
- 3-5 specific deliverables
- Suggested owner (Founder/Marketing/Design/Tech)
- Success criteria

Return as structured markdown with clear week-by-week breakdown.
"""

# KPI Insights Generator Prompt
KPI_INSIGHTS_PROMPT = """You are a Growth Strategy Consultant analyzing KPI projections.

**Projection Details:**
- Starting Weekly Visitors: {base_visitors}
- Conversion Rate: {conversion_rate}%
- Weekly Growth Rate: {growth_rate}%
- Total Projected Signups (12 weeks): {total_signups}
- Brand Type: {brand_type}

**Your Task:**
Provide actionable strategic insights about these projections.

**Analysis Structure:**

## 1. Reality Check
Assess if these goals are realistic, ambitious, or conservative for a {brand_type} launch. Provide context.

## 2. Conversion Optimization
Give 3 specific, tactical recommendations to improve the conversion rate. Be practical and actionable.

## 3. Growth Strategy
Suggest 2-3 proven channels to achieve the projected growth rate for this brand type.

## 4. Risk Factors
Identify 3 potential risks or challenges that could prevent achieving these numbers.

## 5. Key Milestones
Recommend 3 specific milestones to track as leading indicators of success.

Keep the tone professional but encouraging. Focus on actionable insights, not theory.
Return as well-formatted markdown.
"""

# Refinement Prompt (for user feedback iteration)
REFINEMENT_PROMPT = """You are a Brand Copywriter helping refine brand content based on user feedback.

**Context:** {context}

**Original Text:**
{original_text}

**User Feedback:**
{user_feedback}

**Your Task:**
Revise the text incorporating the user's feedback while:
1. Maintaining brand consistency and voice
2. Keeping similar length (±20% of original)
3. Preserving the core message and intent
4. Making it more impactful and polished
5. Ensuring it aligns with the overall brand strategy

Return ONLY the revised text, no explanations or meta-commentary.
"""

# One-Pager Copy Generator Prompt
ONE_PAGER_PROMPT = """You are a Marketing Copywriter creating a compelling one-page brand summary.

**Brand Information:**
- Company: {company_name}
- Vision: {vision}
- Mission: {mission}
- Target Audience: {target_audience}
- Core Problem: {core_problem}
- Positioning: {positioning}
- Values: {values}

**Your Task:**
Write compelling copy for a one-page brand overview that can be used with investors, partners, or early customers.

**Sections to Include:**

### Headline
Punchy, benefit-driven statement (1 sentence)

### The Problem
Describe the pain point (2-3 sentences)

### Our Solution
How we solve it differently (2-3 sentences)

### Why Now
Market timing and opportunity (2-3 sentences)

### Our Approach
Unique methodology or differentiators (3-4 bullet points)

### Target Customer
Who this is for (2 sentences)

### Vision
Where we're headed (1-2 sentences)

Keep the tone aligned with the brand voice. Make it scannable and compelling.
Return as markdown format ready to use.
"""

# Email Signature Prompt
EMAIL_SIGNATURE_PROMPT = """You are creating a professional email signature.

**Details:**
- Company: {company_name}
- Website: {website}
- Positioning: {positioning_snippet}

**Generate an HTML email signature template that includes:**
- Name placeholder
- Title placeholder
- Company name
- One-line positioning statement
- Contact info placeholders (email, phone)
- Website link
- Optional: LinkedIn/Social links

Keep it clean, professional, and not overly designed. Return as HTML code.
"""

# Helper function to format competitor list
def format_competitors_list(competitors: list) -> str:
    """Format list of competitors for prompt."""
    if not competitors:
        return "No specific competitors identified yet."
    return "\n".join(f"- {comp}" for comp in competitors)

# Helper function to format values list
def format_values_list(values: list) -> str:
    """Format list of values for prompt."""
    if not values:
        return "Not defined yet."
    return "\n".join(f"- {val}" for val in values)
