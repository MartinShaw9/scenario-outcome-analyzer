#!/usr/bin/env python3
"""
Business Scenario Examples
Demonstrates the analyzer with various business situations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenario_analyzer import ScenarioAnalyzer
import json

def run_business_examples():
    """Run various business scenario examples"""
    
    analyzer = ScenarioAnalyzer()
    
    scenarios = [
        {
            "title": "🚀 Startup Launch",
            "situation": """
            I'm planning to launch a SaaS platform for restaurant management in India. 
            The platform will handle inventory, orders, staff scheduling, and customer analytics. 
            I have 2 co-founders (tech + marketing background), $200K funding, and 6 months runway. 
            The restaurant industry is recovering post-COVID but highly competitive.
            """,
            "context": {
                "industry": "Technology/Food Service",
                "timeline": "Short-term",
                "budget": "Medium",
                "risk_tolerance": "Aggressive"
            }
        },
        
        {
            "title": "📈 Market Expansion",
            "situation": """
            Our e-commerce company has been successful in North India for 3 years. 
            We're considering expanding to South India markets (Bangalore, Chennai, Hyderabad). 
            This requires $500K investment, hiring 50+ people, and setting up new logistics. 
            Competition is fierce with established players like Flipkart and Amazon.
            """,
            "context": {
                "industry": "E-commerce",
                "timeline": "Medium-term",
                "budget": "High",
                "risk_tolerance": "Moderate"
            }
        },
        
        {
            "title": "🤖 AI Integration",
            "situation": """
            Our manufacturing company wants to implement AI for predictive maintenance 
            and quality control. Initial investment is $1M, requires training 100+ employees, 
            and may disrupt current operations for 6 months. Expected ROI is 25% annually 
            but technology adoption risks are high.
            """,
            "context": {
                "industry": "Manufacturing",
                "timeline": "Long-term",
                "budget": "Very High",
                "risk_tolerance": "Conservative"
            }
        },
        
        {
            "title": "🏢 Office vs Remote",
            "situation": """
            Post-pandemic, our 200-employee software company is deciding between 
            returning to office, staying fully remote, or adopting hybrid model. 
            Office lease costs $50K/month, but productivity and culture concerns exist 
            with remote work. Employee preferences are mixed.
            """,
            "context": {
                "industry": "Technology",
                "timeline": "Immediate",
                "budget": "Medium",
                "risk_tolerance": "Moderate"
            }
        },
        
        {
            "title": "💰 Funding Round",
            "situation": """
            Our fintech startup needs Series A funding ($5M) to scale operations. 
            We have strong user growth (100K+ users) but limited revenue ($50K/month). 
            Market conditions are tough, and we have 8 months of runway left. 
            Alternative is to bootstrap and grow slower.
            """,
            "context": {
                "industry": "Fintech",
                "timeline": "Immediate",
                "budget": "High",
                "risk_tolerance": "Aggressive"
            }
        }
    ]
    
    print("🎯 BUSINESS SCENARIO ANALYSIS EXAMPLES")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{scenario['title']}")
        print("-" * 40)
        
        try:
            analysis = analyzer.analyze(scenario['situation'], scenario['context'])
            
            # Display key insights
            print(f"📊 Generated {len(analysis.outcomes)} possible outcomes")
            
            # Show top 2 outcomes
            sorted_outcomes = sorted(analysis.outcomes, key=lambda x: x.probability, reverse=True)
            
            print("\n🎯 TOP OUTCOMES:")
            for j, outcome in enumerate(sorted_outcomes[:2], 1):
                print(f"\n{j}. {outcome.description}")
                print(f"   📈 Probability: {outcome.probability:.1%}")
                print(f"   💥 Impact: {outcome.impact_level}")
                print(f"   ⏱️  Timeline: {outcome.timeline}")
            
            # Show key recommendations
            print(f"\n💡 KEY RECOMMENDATIONS:")
            for rec in analysis.recommendations[:3]:
                print(f"   • {rec}")
            
            # Save detailed analysis
            filename = f"analysis_{i}_{scenario['title'].replace('🚀', '').replace('📈', '').replace('🤖', '').replace('🏢', '').replace('💰', '').strip().replace(' ', '_').lower()}.json"
            
            with open(f"examples/{filename}", 'w') as f:
                json.dump({
                    'title': scenario['title'],
                    'situation': scenario['situation'],
                    'context': scenario['context'],
                    'analysis': {
                        'outcomes': [
                            {
                                'description': o.description,
                                'probability': o.probability,
                                'impact_level': o.impact_level,
                                'risk_factors': o.risk_factors,
                                'opportunities': o.opportunities,
                                'timeline': o.timeline,
                                'confidence_score': o.confidence_score
                            }
                            for o in analysis.outcomes
                        ],
                        'key_variables': analysis.key_variables,
                        'recommendations': analysis.recommendations,
                        'context_factors': analysis.context_factors
                    }
                }, f, indent=2)
            
            print(f"   📁 Detailed analysis saved to: examples/{filename}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        
        print("\n" + "="*60)
    
    print("\n✅ All business scenario examples completed!")
    print("📁 Check the examples/ directory for detailed JSON outputs")

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    run_business_examples()