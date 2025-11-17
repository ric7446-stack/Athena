"""
Essay Analysis and Improvement Tool
Analyzes marketing plan essays for consistency, formatting, and quality issues
"""

import re
import json
from typing import Dict, List, Tuple
from collections import defaultdict


class EssayAnalyzer:
    def __init__(self, essay_text: str):
        self.essay_text = essay_text
        self.issues = defaultdict(list)
        self.statistics = {}
        
    def analyze_all(self) -> Dict:
        """Run all analysis checks"""
        self.check_consistency()
        self.check_formatting()
        self.check_writing_quality()
        self.check_structure()
        self.check_citations()
        self.calculate_statistics()
        
        return {
            'issues': dict(self.issues),
            'statistics': self.statistics,
            'severity_summary': self.get_severity_summary()
        }
    
    def check_consistency(self):
        """Check for consistency issues in the essay"""
        
        # Check for inconsistent terminology
        terms_variations = {
            'Café Quindío': ['Cafe Quindio', 'cafe quindio', 'Café Quindio'],
            'farm-to-cup': ['farm to cup', 'Farm-to-Cup', 'Farm to Cup'],
            'e-commerce': ['ecommerce', 'E-commerce', 'e commerce']
        }
        
        for correct_term, variations in terms_variations.items():
            for variation in variations:
                if variation in self.essay_text and variation != correct_term:
                    self.issues['consistency'].append({
                        'type': 'Inconsistent terminology',
                        'issue': f'Found "{variation}" instead of "{correct_term}"',
                        'severity': 'medium'
                    })
        
        # Check for inconsistent number formatting
        number_patterns = re.findall(r'\$[\d,]+\.?\d*\s*(?:CAD|billion|million)?', self.essay_text)
        if number_patterns:
            # Check if CAD is placed consistently
            cad_before = len(re.findall(r'CAD\s+\$', self.essay_text))
            cad_after = len(re.findall(r'\$[\d,]+\.?\d*\s+CAD', self.essay_text))
            
            if cad_before > 0 and cad_after > 0:
                self.issues['consistency'].append({
                    'type': 'Inconsistent currency format',
                    'issue': f'Currency format varies: CAD before $ ({cad_before} times) vs after $ ({cad_after} times)',
                    'severity': 'medium'
                })
        
        # Check for incomplete sections
        if 'Expected results' in self.essay_text and not re.search(r'Expected results.*?\n.*?[A-Za-z]', self.essay_text):
            self.issues['consistency'].append({
                'type': 'Incomplete section',
                'issue': 'Section "1.5 Expected results" appears to be empty',
                'severity': 'high'
            })
        
        if 'Vision' in self.essay_text and not re.search(r'2\.2 Vision.*?\n.*?[A-Za-z]', self.essay_text):
            self.issues['consistency'].append({
                'type': 'Incomplete section',
                'issue': 'Section "2.2 Vision" appears to be empty',
                'severity': 'high'
            })
    
    def check_formatting(self):
        """Check for formatting issues"""
        
        # Check for inconsistent heading numbering
        headings = re.findall(r'^(\d+\.\d+(?:\.\d+)?)\s+(.+)$', self.essay_text, re.MULTILINE)
        
        if headings:
            prev_num = None
            for num, title in headings:
                parts = num.split('.')
                if prev_num:
                    prev_parts = prev_num.split('.')
                    # Check logical progression
                    if len(parts) == len(prev_parts):
                        if int(parts[-1]) != int(prev_parts[-1]) + 1:
                            self.issues['formatting'].append({
                                'type': 'Heading numbering',
                                'issue': f'Heading {num} does not follow {prev_num} logically',
                                'severity': 'low'
                            })
                prev_num = num
        
        # Check for spacing issues
        double_spaces = len(re.findall(r'  +', self.essay_text))
        if double_spaces > 10:
            self.issues['formatting'].append({
                'type': 'Spacing',
                'issue': f'Found {double_spaces} instances of multiple consecutive spaces',
                'severity': 'low'
            })
        
        # Check for inconsistent list formatting
        arrow_lists = len(re.findall(r'->', self.essay_text))
        bullet_lists = len(re.findall(r'^\s*[-•]\s', self.essay_text, re.MULTILINE))
        
        if arrow_lists > 0 and bullet_lists > 0:
            self.issues['formatting'].append({
                'type': 'List formatting',
                'issue': f'Mixed list styles: arrows ({arrow_lists}) and bullets ({bullet_lists})',
                'severity': 'medium'
            })
        
        # Check for proper citation formatting
        citations = re.findall(r'\([^)]*\d{4}[^)]*\)', self.essay_text)
        for citation in citations:
            if not re.match(r'\([A-Za-z\s&]+,\s*\d{4}[a-z]?\)', citation):
                self.issues['formatting'].append({
                    'type': 'Citation format',
                    'issue': f'Potentially malformed citation: {citation}',
                    'severity': 'low'
                })
    
    def check_writing_quality(self):
        """Check for writing quality issues"""
        
        # Check for overly long sentences (>40 words)
        sentences = re.split(r'[.!?]+', self.essay_text)
        long_sentences = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 40:
                long_sentences.append({
                    'length': len(words),
                    'preview': ' '.join(words[:15]) + '...'
                })
        
        if long_sentences:
            self.issues['writing_quality'].append({
                'type': 'Sentence length',
                'issue': f'Found {len(long_sentences)} sentences with >40 words',
                'examples': long_sentences[:3],
                'severity': 'medium'
            })
        
        # Check for passive voice indicators
        passive_indicators = ['is being', 'was being', 'has been', 'have been', 'will be']
        passive_count = sum(self.essay_text.lower().count(indicator) for indicator in passive_indicators)
        
        if passive_count > 15:
            self.issues['writing_quality'].append({
                'type': 'Passive voice',
                'issue': f'High use of passive voice ({passive_count} instances)',
                'severity': 'low'
            })
        
        # Check for informal language
        informal_phrases = [
            'Well,', 'So is it', 'let´s get', 'Not only that but',
            'Well, therefore', 'It is quite common'
        ]
        
        for phrase in informal_phrases:
            if phrase in self.essay_text:
                self.issues['writing_quality'].append({
                    'type': 'Informal language',
                    'issue': f'Informal phrase found: "{phrase}"',
                    'severity': 'medium'
                })
        
        # Check for contractions (should be avoided in formal writing)
        contractions = re.findall(r"\b\w+'\w+\b", self.essay_text)
        if contractions:
            self.issues['writing_quality'].append({
                'type': 'Contractions',
                'issue': f'Found {len(contractions)} contractions in formal document',
                'examples': list(set(contractions))[:5],
                'severity': 'medium'
            })
        
        # Check for vague language
        vague_terms = ['quite', 'very', 'really', 'somewhat', 'fairly']
        vague_count = sum(self.essay_text.lower().count(f' {term} ') for term in vague_terms)
        
        if vague_count > 5:
            self.issues['writing_quality'].append({
                'type': 'Vague language',
                'issue': f'Overuse of vague qualifiers ({vague_count} instances)',
                'severity': 'low'
            })
    
    def check_structure(self):
        """Check document structure and organization"""
        
        # Check for logical flow of sections
        required_sections = [
            '1.0', '2.0', '3.0', '4.0'
        ]
        
        for section in required_sections:
            if section not in self.essay_text:
                self.issues['structure'].append({
                    'type': 'Missing section',
                    'issue': f'Required section {section} not found',
                    'severity': 'high'
                })
        
        # Check for orphaned subsections
        subsection_pattern = r'(\d+\.\d+\.\d+)\s'
        subsections = re.findall(subsection_pattern, self.essay_text)
        
        for subsection in subsections:
            parent = '.'.join(subsection.split('.')[:2])
            if parent not in self.essay_text:
                self.issues['structure'].append({
                    'type': 'Orphaned subsection',
                    'issue': f'Subsection {subsection} exists without parent {parent}',
                    'severity': 'medium'
                })
        
        # Check for abrupt transitions
        transition_words = ['however', 'therefore', 'additionally', 'furthermore', 'conversely']
        paragraphs = self.essay_text.split('\n\n')
        
        transitions_count = 0
        for para in paragraphs:
            if any(para.lower().startswith(word) for word in transition_words):
                transitions_count += 1
        
        if transitions_count < len(paragraphs) * 0.2:
            self.issues['structure'].append({
                'type': 'Transitions',
                'issue': 'Limited use of transition words between paragraphs',
                'severity': 'low'
            })
    
    def check_citations(self):
        """Check citation consistency and completeness"""
        
        # Extract all citations
        citations = re.findall(r'\(([^)]*\d{4}[a-z]?[^)]*)\)', self.essay_text)
        
        # Check for consistent citation style
        citation_styles = {
            'author_year': 0,
            'other': 0
        }
        
        for citation in citations:
            if re.match(r'^[A-Za-z\s&]+,\s*\d{4}[a-z]?$', citation):
                citation_styles['author_year'] += 1
            else:
                citation_styles['other'] += 1
        
        if citation_styles['author_year'] > 0 and citation_styles['other'] > 0:
            self.issues['citations'].append({
                'type': 'Citation style inconsistency',
                'issue': f'Mixed citation styles detected',
                'severity': 'medium'
            })
        
        # Check for repeated citations
        citation_counts = defaultdict(int)
        for citation in citations:
            citation_counts[citation] += 1
        
        # Most cited sources
        most_cited = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        self.statistics['most_cited_sources'] = [
            {'source': source, 'count': count} for source, count in most_cited
        ]
    
    def calculate_statistics(self):
        """Calculate document statistics"""
        
        # Word count
        words = self.essay_text.split()
        self.statistics['word_count'] = len(words)
        
        # Sentence count
        sentences = re.split(r'[.!?]+', self.essay_text)
        sentences = [s for s in sentences if s.strip()]
        self.statistics['sentence_count'] = len(sentences)
        
        # Average sentence length
        if sentences:
            self.statistics['avg_sentence_length'] = len(words) / len(sentences)
        
        # Paragraph count
        paragraphs = [p for p in self.essay_text.split('\n\n') if p.strip()]
        self.statistics['paragraph_count'] = len(paragraphs)
        
        # Section count
        sections = re.findall(r'^\d+\.\d+', self.essay_text, re.MULTILINE)
        self.statistics['section_count'] = len(set(sections))
        
        # Citation count
        citations = re.findall(r'\([^)]*\d{4}[^)]*\)', self.essay_text)
        self.statistics['citation_count'] = len(citations)
        
        # Readability metrics
        if sentences and words:
            # Simple readability score (words per sentence)
            self.statistics['readability_score'] = 'Complex' if self.statistics['avg_sentence_length'] > 25 else 'Moderate' if self.statistics['avg_sentence_length'] > 15 else 'Simple'
    
    def get_severity_summary(self) -> Dict:
        """Get summary of issues by severity"""
        summary = {'high': 0, 'medium': 0, 'low': 0}
        
        for category, issues_list in self.issues.items():
            for issue in issues_list:
                severity = issue.get('severity', 'low')
                summary[severity] += 1
        
        return summary
    
    def generate_report(self) -> str:
        """Generate a formatted analysis report"""
        
        analysis = self.analyze_all()
        
        report = []
        report.append("=" * 80)
        report.append("ESSAY ANALYSIS REPORT")
        report.append("Café Quindío Marketing Plan - Retail in Canada Analysis")
        report.append("=" * 80)
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)
        severity = analysis['severity_summary']
        total_issues = sum(severity.values())
        report.append(f"Total Issues Found: {total_issues}")
        report.append(f"  - High Severity: {severity['high']}")
        report.append(f"  - Medium Severity: {severity['medium']}")
        report.append(f"  - Low Severity: {severity['low']}")
        report.append("")
        
        # Document Statistics
        report.append("DOCUMENT STATISTICS")
        report.append("-" * 80)
        stats = analysis['statistics']
        report.append(f"Word Count: {stats.get('word_count', 0):,}")
        report.append(f"Sentence Count: {stats.get('sentence_count', 0):,}")
        report.append(f"Average Sentence Length: {stats.get('avg_sentence_length', 0):.1f} words")
        report.append(f"Paragraph Count: {stats.get('paragraph_count', 0)}")
        report.append(f"Section Count: {stats.get('section_count', 0)}")
        report.append(f"Citation Count: {stats.get('citation_count', 0)}")
        report.append(f"Readability: {stats.get('readability_score', 'N/A')}")
        report.append("")
        
        # Detailed Issues
        report.append("DETAILED ISSUES BY CATEGORY")
        report.append("=" * 80)
        
        for category, issues_list in analysis['issues'].items():
            if issues_list:
                report.append("")
                report.append(f"{category.upper().replace('_', ' ')}")
                report.append("-" * 80)
                
                for i, issue in enumerate(issues_list, 1):
                    severity_marker = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
                    report.append(f"{i}. [{severity_marker} {issue['severity'].upper()}] {issue['type']}")
                    report.append(f"   Issue: {issue['issue']}")
                    
                    if 'examples' in issue:
                        report.append(f"   Examples: {issue['examples']}")
                    
                    report.append("")
        
        # Recommendations
        report.append("")
        report.append("KEY RECOMMENDATIONS")
        report.append("=" * 80)
        
        recommendations = self.generate_recommendations(analysis)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Check for high severity issues
        if analysis['severity_summary']['high'] > 0:
            recommendations.append(
                "CRITICAL: Complete all empty sections (1.5 Expected Results, 2.2 Vision) "
                "before finalizing the document."
            )
        
        # Check for consistency issues
        if 'consistency' in analysis['issues'] and analysis['issues']['consistency']:
            recommendations.append(
                "Standardize terminology throughout the document. Use 'Café Quindío' consistently "
                "and maintain uniform currency formatting (recommend: CAD $X.XX format)."
            )
        
        # Check for writing quality
        if 'writing_quality' in analysis['issues']:
            informal_issues = [i for i in analysis['issues']['writing_quality'] 
                             if i['type'] == 'Informal language']
            if informal_issues:
                recommendations.append(
                    "Replace informal phrases with formal academic language. Avoid conversational "
                    "starters like 'Well,' 'So,' and rhetorical questions in formal sections."
                )
        
        # Check sentence length
        if analysis['statistics'].get('avg_sentence_length', 0) > 25:
            recommendations.append(
                "Break down complex sentences. Average sentence length is high; aim for "
                "15-20 words per sentence for better readability."
            )
        
        # Check formatting
        if 'formatting' in analysis['issues'] and analysis['issues']['formatting']:
            recommendations.append(
                "Standardize formatting: use consistent list styles (bullets vs. arrows), "
                "ensure proper spacing, and verify all heading numbers follow logical sequence."
            )
        
        # Structure recommendations
        recommendations.append(
            "Add clear transition sentences between major sections to improve flow and "
            "guide the reader through your argument."
        )
        
        recommendations.append(
            "Consider adding visual elements (tables, charts) to break up dense text, "
            "especially in the SWOT and competitive analysis sections."
        )
        
        recommendations.append(
            "Ensure all figures referenced (e.g., 'Figure 3 Target Customer Profile') "
            "are properly included and numbered sequentially."
        )
        
        return recommendations


def main():
    """Main execution function"""
    
    # Read the essay content
    essay_file = '/vercel/sandbox/original_essay.txt'
    
    try:
        with open(essay_file, 'r', encoding='utf-8') as f:
            essay_text = f.read()
    except FileNotFoundError:
        print(f"Error: Essay file not found at {essay_file}")
        print("Please ensure the essay text is saved in 'original_essay.txt'")
        return
    
    # Create analyzer
    analyzer = EssayAnalyzer(essay_text)
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save report
    report_file = '/vercel/sandbox/essay_analysis_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Analysis complete!")
    print(f"📄 Report saved to: {report_file}")
    print("")
    print(report)
    
    # Save detailed JSON analysis
    analysis_data = analyzer.analyze_all()
    json_file = '/vercel/sandbox/essay_analysis_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n📊 Detailed data saved to: {json_file}")


if __name__ == "__main__":
    main()
