#!/usr/bin/env python3
"""
Scenario Outcome Analyzer
AI agent that interprets situations and generates multiple possible outcomes
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from openai import OpenAI

@dataclass
class Outcome:
    """Represents a single possible outcome"""
    description: str
    probability: float
    impact_level: str  # "Low", "Medium", "High"
    risk_factors: List[str]
    opportunities: List[str]
    timeline: str
    confidence_score: float

@dataclass
class ScenarioAnalysis:
    """Complete analysis of a scenario"""
    situation: str
    context_factors: List[str]
    outcomes: List[Outcome]
    key_variables: List[str]
    recommendations: List[str]
    analysis_timestamp: str
    
    def formatted_output(self) -> str:
        """Returns formatted analysis for display"""
        output = f"""
🎯 SCENARIO ANALYSIS
{'='*50}

📋 SITUATION: {self.situation}

🔍 KEY CONTEXT FACTORS:
{chr(10).join(f"• {factor}" for factor in self.context_factors)}

📊 POSSIBLE OUTCOMES:
"""
        for i, outcome in enumerate(self.outcomes, 1):
            output += f"""
{i}. {outcome.description}
   📈 Probability: {outcome.probability:.1%}
   💥 Impact: {outcome.impact_level}
   ⚠️  Risks: {', '.join(outcome.risk_factors)}
   🎯 Opportunities: {', '.join(outcome.opportunities)}
   ⏱️  Timeline: {outcome.timeline}
   🎲 Confidence: {outcome.confidence_score:.1%}
"""

        output += f"""
🔑 KEY VARIABLES:
{chr(10).join(f"• {var}" for var in self.key_variables)}

💡 RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in self.recommendations)}

📅 Analysis Date: {self.analysis_timestamp}
"""
        return output

class ScenarioAnalyzer:
    """Main analyzer class"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = model
        
    def analyze(self, situation: str, context: Optional[Dict] = None) -> ScenarioAnalysis:
        """
        Analyze a situation and generate possible outcomes
        
        Args:
            situation: Description of the situation to analyze
            context: Additional context information
            
        Returns:
            ScenarioAnalysis object with complete analysis
        """
        
        # Extract context factors
        context_factors = self._extract_context_factors(situation, context)
        
        # Generate outcomes using AI
        outcomes = self._generate_outcomes(situation, context_factors)
        
        # Identify key variables
        key_variables = self._identify_key_variables(situation, outcomes)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(situation, outcomes)
        
        return ScenarioAnalysis(
            situation=situation,
            context_factors=context_factors,
            outcomes=outcomes,
            key_variables=key_variables,
            recommendations=recommendations,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _extract_context_factors(self, situation: str, context: Optional[Dict]) -> List[str]:
        """Extract relevant context factors from situation"""
        factors = []
        
        # Basic pattern matching for common factors
        if re.search(r'\b(business|company|startup)\b', situation.lower()):
            factors.append("Business/Commercial context")
        if re.search(r'\b(market|economy|financial)\b', situation.lower()):
            factors.append("Economic factors")
        if re.search(r'\b(team|people|employee)\b', situation.lower()):
            factors.append("Human resources")
        if re.search(r'\b(technology|tech|digital)\b', situation.lower()):
            factors.append("Technology factors")
        if re.search(r'\b(time|deadline|urgent)\b', situation.lower()):
            factors.append("Time constraints")
        
        # Add context from parameters
        if context:
            for key, value in context.items():
                factors.append(f"{key}: {value}")
                
        return factors if factors else ["General situational context"]
    
    def _generate_outcomes(self, situation: str, context_factors: List[str]) -> List[Outcome]:
        """Generate possible outcomes using AI or rule-based logic"""
        
        if self.client:
            return self._ai_generate_outcomes(situation, context_factors)
        else:
            return self._rule_based_outcomes(situation, context_factors)
    
    def _ai_generate_outcomes(self, situation: str, context_factors: List[str]) -> List[Outcome]:
        """Use AI to generate sophisticated outcomes"""
        
        prompt = f"""
        Analyze this situation and generate 4-6 possible outcomes:
        
        SITUATION: {situation}
        
        CONTEXT: {', '.join(context_factors)}
        
        For each outcome, provide:
        1. Clear description
        2. Probability (0-1)
        3. Impact level (Low/Medium/High)
        4. Risk factors (list)
        5. Opportunities (list)
        6. Timeline estimate
        7. Confidence score (0-1)
        
        Return as JSON array of outcomes.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Parse AI response and convert to Outcome objects
            ai_outcomes = json.loads(response.choices[0].message.content)
            return [Outcome(**outcome) for outcome in ai_outcomes]
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._rule_based_outcomes(situation, context_factors)
    
    def _rule_based_outcomes(self, situation: str, context_factors: List[str]) -> List[Outcome]:
        """Generate outcomes using rule-based logic as fallback"""
        
        outcomes = []
        
        # Best case scenario
        outcomes.append(Outcome(
            description="Optimal outcome - all factors align favorably",
            probability=0.25,
            impact_level="High",
            risk_factors=["Overconfidence", "External disruptions"],
            opportunities=["Maximum benefit realization", "Positive momentum"],
            timeline="Short to medium term",
            confidence_score=0.7
        ))
        
        # Most likely scenario
        outcomes.append(Outcome(
            description="Expected outcome - moderate success with some challenges",
            probability=0.45,
            impact_level="Medium",
            risk_factors=["Resource constraints", "Execution challenges"],
            opportunities=["Learning opportunities", "Incremental progress"],
            timeline="Medium term",
            confidence_score=0.85
        ))
        
        # Challenging scenario
        outcomes.append(Outcome(
            description="Difficult outcome - significant obstacles encountered",
            probability=0.25,
            impact_level="Medium",
            risk_factors=["Major setbacks", "Resource depletion"],
            opportunities=["Resilience building", "Alternative paths"],
            timeline="Extended timeline",
            confidence_score=0.75
        ))
        
        # Worst case scenario
        outcomes.append(Outcome(
            description="Adverse outcome - multiple failures compound",
            probability=0.05,
            impact_level="High",
            risk_factors=["Complete failure", "Reputation damage"],
            opportunities=["Lessons learned", "Fresh start potential"],
            timeline="Long term recovery",
            confidence_score=0.6
        ))
        
        return outcomes
    
    def _identify_key_variables(self, situation: str, outcomes: List[Outcome]) -> List[str]:
        """Identify key variables that influence outcomes"""
        
        variables = []
        
        # Extract from situation
        if "decision" in situation.lower():
            variables.append("Decision quality and timing")
        if "resource" in situation.lower():
            variables.append("Resource availability")
        if "market" in situation.lower():
            variables.append("Market conditions")
        if "team" in situation.lower():
            variables.append("Team performance and dynamics")
        
        # Extract from outcomes
        all_risks = []
        for outcome in outcomes:
            all_risks.extend(outcome.risk_factors)
        
        # Convert common risks to variables
        if any("resource" in risk.lower() for risk in all_risks):
            variables.append("Resource management")
        if any("execution" in risk.lower() for risk in all_risks):
            variables.append("Execution capability")
        if any("external" in risk.lower() for risk in all_risks):
            variables.append("External environment")
            
        return variables if variables else ["Situational dynamics", "External factors"]
    
    def _generate_recommendations(self, situation: str, outcomes: List[Outcome]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # High probability outcome focus
        high_prob_outcomes = [o for o in outcomes if o.probability > 0.3]
        if high_prob_outcomes:
            recommendations.append(f"Prepare primarily for: {high_prob_outcomes[0].description}")
        
        # Risk mitigation
        all_risks = []
        for outcome in outcomes:
            all_risks.extend(outcome.risk_factors)
        common_risks = list(set(all_risks))[:3]
        
        for risk in common_risks:
            recommendations.append(f"Mitigate risk: {risk}")
        
        # Opportunity capture
        all_opportunities = []
        for outcome in outcomes:
            all_opportunities.extend(outcome.opportunities)
        common_opportunities = list(set(all_opportunities))[:2]
        
        for opp in common_opportunities:
            recommendations.append(f"Leverage opportunity: {opp}")
        
        # General advice
        recommendations.append("Monitor key variables closely")
        recommendations.append("Maintain flexibility for scenario pivots")
        
        return recommendations

def main():
    """Demo the analyzer"""
    analyzer = ScenarioAnalyzer()
    
    # Example scenario
    situation = """
    I'm considering launching a new AI-powered mobile app for small businesses in India. 
    The app would help with inventory management and customer analytics. 
    I have a team of 3 developers and $50,000 in funding.
    """
    
    analysis = analyzer.analyze(situation)
    print(analysis.formatted_output())
    
    # Save to file
    with open('analysis_output.json', 'w') as f:
        json.dump(asdict(analysis), f, indent=2)
    
    print("\n✅ Analysis saved to analysis_output.json")

if __name__ == "__main__":
    main()