#!/usr/bin/env python
# scripts/init_data.py

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import DATA_DIR
from backend.utils import ensure_data_dir_exists

# Sample business documents for testing
SAMPLE_DOCUMENTS = [
    {
        "filename": "financial_report_q1_2024.txt",
        "content": """
Financial Performance Report - Q1 2024

Executive Summary:
In the first quarter of 2024, our company demonstrated strong financial performance with revenue growth of 15% year-over-year. EBITDA margins expanded to 28%, up from 24% in the same period last year. Operating cash flow increased by 22%, enabling accelerated debt repayment and strategic investments in R&D.

Revenue Analysis:
Total revenue reached $42.8 million, compared to $37.2 million in Q1 2023. The growth was primarily driven by:
1. Expanded market share in North America (+18%)
2. Successful launch of our premium service tier (+$2.3M in new revenue)
3. Increased customer retention rate (87%, up from 82%)

The subscription-based revenue model continues to provide stability, with recurring revenue now accounting for 73% of total revenue.

Expense Management:
Operating expenses were $30.1 million, representing 70.3% of revenue, an improvement from 73.8% in the prior year. Key factors include:
1. Economies of scale in cloud infrastructure (reduced from 12% to 9% of revenue)
2. Improved marketing efficiency with CAC reduced by 15%
3. Partial offset from increased headcount in engineering (+12 FTEs)

Profitability:
Gross profit margin improved to 75%, up from 72% in Q1 2023, primarily due to improved economies of scale and strategic vendor negotiations. Net profit reached $8.4 million, representing a 19.6% margin.

Balance Sheet:
Cash and cash equivalents stand at $28.5 million, up from $24.2 million at the end of 2023. The debt-to-equity ratio improved to 0.35, down from 0.42. Capital expenditures were $3.1 million, focused primarily on infrastructure modernization.

Outlook:
Based on current performance and market conditions, we are raising our full-year guidance:
- Revenue: $175-185 million (previously $165-175 million)
- EBITDA margin: 27-29% (previously 25-27%)
- Free cash flow: $38-42 million (previously $34-38 million)

Risks and Challenges:
1. Increasing competition in the enterprise segment
2. Foreign exchange volatility affecting international revenues
3. Potential regulatory changes in the European market
4. Supply chain constraints affecting hardware component availability
        """
    },
    {
        "filename": "market_research_2024.txt",
        "content": """
Market Research Report: Industry Trends and Opportunities 2024

Executive Summary:
Our comprehensive market analysis reveals significant growth opportunities in the business intelligence and data analytics sector for 2024 and beyond. The global market is projected to reach $43.5 billion by 2026, with a CAGR of 11.2%. Key drivers include increasing adoption of AI-driven analytics, demand for real-time business insights, and the growing importance of data-driven decision making across industries.

Market Segmentation:
1. By Component:
   - Software solutions: 65% of market share
   - Services (consulting, implementation, support): 35%

2. By Deployment:
   - Cloud-based solutions: 72% (growing at 14.8% CAGR)
   - On-premises solutions: 28% (growing at 5.2% CAGR)

3. By End-User:
   - Banking and Financial Services: 24%
   - Healthcare and Life Sciences: 18%
   - Manufacturing: 16%
   - Retail and E-commerce: 15%
   - Others: 27%

Competitive Landscape:
The market remains moderately fragmented with the top 5 players controlling approximately 38% of market share. Key competitive factors include:
- AI and machine learning capabilities
- Ease of integration with existing systems
- Real-time analytics features
- Security and compliance features
- Pricing models and total cost of ownership

Recent entrants are disrupting the market with specialized, industry-specific solutions that offer faster time-to-value compared to traditional platforms.

Customer Needs and Pain Points:
Our survey of 1,500 business decision-makers identified these top challenges:
1. Difficulty integrating data from disparate sources (68%)
2. Lack of skilled personnel to analyze data effectively (62%)
3. Concerns about data security and governance (57%)
4. Need for real-time insights rather than historical reporting (54%)
5. Difficulty measuring ROI from analytics investments (48%)

Technology Trends:
1. Natural Language Processing (NLP) is becoming a standard feature, allowing business users to query data using natural language
2. Automated insights and anomaly detection are reducing the need for manual data exploration
3. Embedded analytics are growing at 18% CAGR as companies integrate analytics directly into operational applications
4. Edge analytics adoption is accelerating with IoT expansion, particularly in manufacturing and logistics

Market Opportunities:
1. Industry-specific solutions with pre-built models for vertical markets
2. Self-service analytics platforms for business users without technical expertise
3. Predictive analytics solutions that deliver forward-looking insights
4. Solutions bridging the gap between data science and business applications
5. Subscription-based pricing models for SME market penetration

Recommendations:
Based on our analysis, we recommend focusing on these strategic priorities:
1. Develop AI-powered automated insights capabilities to differentiate from competitors
2. Create industry-specific solution packages for high-growth verticals (healthcare, financial services)
3. Invest in natural language interfaces to improve accessibility for business users
4. Build robust data governance features to address security concerns
5. Develop integration capabilities to connect with popular enterprise systems
        """
    },
    {
        "filename": "risk_assessment_report.txt",
        "content": """
Comprehensive Risk Assessment Report

Executive Summary:
This risk assessment evaluates the key strategic, operational, financial, and compliance risks facing our organization in the current business environment. The assessment identifies 12 high-priority risks requiring immediate mitigation actions, 8 medium-priority risks needing ongoing monitoring, and 5 low-priority risks that should be periodically reviewed. The most significant risks relate to cybersecurity vulnerabilities, supply chain disruptions, and emerging regulatory requirements.

Strategic Risks:

1. Competitive Disruption
   - Risk Level: High
   - Description: Emerging competitors with innovative business models could capture significant market share.
   - Impact: Potential 15-20% reduction in revenue over 24 months if not addressed.
   - Mitigation Strategies: Enhance innovation pipeline, conduct competitive intelligence program, evaluate strategic acquisitions.

2. Market Volatility
   - Risk Level: Medium
   - Description: Unpredictable shifts in market demand due to economic uncertainty.
   - Impact: Potential 10-15% fluctuation in quarterly revenue.
   - Mitigation Strategies: Diversify product/service offerings, enhance forecasting models, build financial reserves.

3. Talent Acquisition and Retention
   - Risk Level: High
   - Description: Increasingly competitive labor market for specialized technical talent.
   - Impact: Increased hiring costs, delayed product development, knowledge loss.
   - Mitigation Strategies: Enhanced compensation packages, career development programs, improved work environment.

Operational Risks:

4. Cybersecurity Threats
   - Risk Level: Critical
   - Description: Sophisticated cyber attacks targeting intellectual property and customer data.
   - Impact: Potential data breaches costing $5-10M in damages, remediation, and reputational harm.
   - Mitigation Strategies: Security infrastructure upgrades, employee training, incident response planning, cyber insurance.

5. Supply Chain Disruptions
   - Risk Level: High
   - Description: Continued global supply chain instability affecting key components.
   - Impact: Production delays, increased costs, inventory challenges.
   - Mitigation Strategies: Supplier diversification, increased inventory buffers, alternative sourcing plans.

6. Technology Infrastructure Reliability
   - Risk Level: Medium
   - Description: Aging infrastructure components may lead to system outages.
   - Impact: Service disruptions, reduced customer satisfaction, recovery costs.
   - Mitigation Strategies: Infrastructure modernization program, enhanced monitoring, redundancy improvements.

Financial Risks:

7. Foreign Exchange Exposure
   - Risk Level: Medium
   - Description: Volatility in key currency exchange rates affecting revenue and costs.
   - Impact: Potential 3-5% margin impact from unfavorable exchange rate movements.
   - Mitigation Strategies: Hedging strategies, natural hedging through geographic expense matching.

8. Credit Risk Concentration
   - Risk Level: Medium
   - Description: High revenue concentration among small number of enterprise customers.
   - Impact: Significant revenue impact if key customers experience financial distress.
   - Mitigation Strategies: Customer diversification, enhanced credit monitoring, contract term adjustments.

9. Liquidity Management
   - Risk Level: Low
   - Description: Ensuring sufficient cash reserves for growth initiatives and unforeseen challenges.
   - Impact: Potential constraints on strategic investments or crisis response.
   - Mitigation Strategies: Maintain appropriate cash reserves, optimize working capital, ensure credit facility availability.

Compliance Risks:

10. Regulatory Changes
    - Risk Level: High
    - Description: Evolving data privacy and AI regulations across global markets.
    - Impact: Compliance costs, potential penalties, product design constraints.
    - Mitigation Strategies: Regulatory monitoring program, proactive compliance measures, participation in industry policy discussions.

11. Intellectual Property Protection
    - Risk Level: Medium
    - Description: Challenges in protecting proprietary technology across global markets.
    - Impact: Revenue loss from unauthorized use, litigation costs.
    - Mitigation Strategies: Robust patent strategy, enhanced contractual protections, monitoring program.

12. Environmental Compliance
    - Risk Level: Low
    - Description: Increasing environmental reporting and performance requirements.
    - Impact: Reporting costs, potential operational constraints.
    - Mitigation Strategies: Sustainability program enhancement, monitoring regulatory developments.

Risk Governance:
The Risk Management Committee will oversee the implementation of mitigation strategies with quarterly reviews of high-priority risks and semi-annual reviews of medium and low-priority risks. Risk ownership has been assigned to appropriate executives with clear accountability for mitigation actions.

Conclusion:
The organization faces a complex risk landscape requiring proactive management and continuous monitoring. By implementing the recommended mitigation strategies, we expect to reduce the potential impact of high-priority risks by approximately 40-60% over the next 12 months.
        """
    }
]

def create_sample_data():
    """Create sample data files for testing."""
    ensure_data_dir_exists(DATA_DIR)
    
    print(f"Creating sample data files in: {DATA_DIR}")
    
    for document in SAMPLE_DOCUMENTS:
        file_path = os.path.join(DATA_DIR, document["filename"])
        with open(file_path, "w") as f:
            f.write(document["content"])
        print(f"Created: {document['filename']}")
    
    print(f"Created {len(SAMPLE_DOCUMENTS)} sample documents.")

if __name__ == "__main__":
    create_sample_data()