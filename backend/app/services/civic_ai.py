"""
Civic Issue Specific AI Services
AI components that actually help with civic issue detection and resolution
"""

import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import random


"""
Unified Civic Issue Classification Engine
-----------------------------------------
Each category has:
  - `classes`:   Specific subclass labels for the issue type
  - `triggers`:  HIGH-WEIGHT keywords (single words AND short phrases) that strongly signal this category
  - `hints`:     LOWER-WEIGHT context words that support classification but aren't conclusive alone
  - `dept`:      Default department to route to
"""

# ---------------------------------------------------------------------------
# CATEGORY DEFINITIONS
# Each `trigger` keyword that matches gives +10 points.
# Each `hint`    keyword that matches gives +3  points.
# Subclass selection is done by matching trigger/hint words inside subclass names.
# ---------------------------------------------------------------------------
CIVIC_ISSUE_TYPES = {
    'roads': {
        'classes': ['pothole', 'road_crack', 'manhole', 'speed_breaker', 'road_waterlogging', 'collapsed_road', 'road_damage'],
        'triggers': [
            'pothole', 'potholes', 'road crack', 'manhole', 'speed breaker', 'speedbreaker',
            'asphalt', 'pavement', 'tarmac', 'road damage', 'road broken', 'broken road',
            'highway damage', 'street crack', 'waterlogged road', 'road flooding'
        ],
        'hints': ['road', 'street', 'lane', 'highway', 'pathway', 'footpath', 'sidewalk', 'pit', 'hole'],
        'severity_factors': ['size', 'depth', 'location', 'traffic'],
        'dept': 'Public Works Department (PWD)'
    },
    'water': {
        'classes': ['water_leak', 'clogged_drain', 'flooding', 'sewage_overflow', 'pipeline_burst', 'contaminated_water', 'no_water_supply'],
        'triggers': [
            'water leak', 'pipe leak', 'pipe burst', 'burst pipe', 'sewage', 'flooding',
            'water logging', 'waterlogging', 'drain overflow', 'clogged drain', 'open drain',
            'water supply', 'no water', 'contaminated water', 'dirty water', 'stagnant water',
            'overflowing drain', 'drainage', 'manhole overflow', 'sewer'
        ],
        'hints': ['water', 'drain', 'pipe', 'flood', 'overflow', 'leak', 'gutter', 'tap', 'well', 'tank', 'wet', 'submerged'],
        'severity_factors': ['flow_rate', 'duration', 'area_affected'],
        'dept': 'Water Department'
    },
    'sanitation': {
        'classes': ['garbage_heap', 'overflowing_dustbin', 'dead_animal', 'open_defecation', 'hazardous_waste', 'dirty_public_area'],
        'triggers': [
            'garbage', 'garbage heap', 'trash', 'waste dump', 'litter', 'overflowing bin',
            'dustbin', 'dumpster', 'open dump', 'rotting', 'stench', 'filth', 'dirty area',
            'dead animal', 'open defecation', 'waste disposal', 'rubbish heap', 'refuse'
        ],
        'hints': ['waste', 'smell', 'unclean', 'dump', 'bin', 'debris', 'messy', 'unhygienic', 'junk'],
        'severity_factors': ['size', 'smell_intensity', 'health_risk'],
        'dept': 'Sanitation Department'
    },
    'electricity': {
        'classes': ['broken_street_light', 'dangling_wire', 'exposed_live_wire', 'electric_pole_damage', 'transformer_issue', 'power_outage'],
        'triggers': [
            'street light', 'streetlight', 'light pole', 'broken light', 'light not working',
            'light out', 'no light', 'dark street', 'electric wire', 'hanging wire',
            'dangling wire', 'live wire', 'exposed wire', 'broken pole', 'light pole broken',
            'power cut', 'electricity gone', 'transformer', 'short circuit', 'electric shock',
            'sparking wire', 'loose wire', 'fallen wire', 'wire fallen'
        ],
        'hints': ['light', 'pole', 'electric', 'power', 'wire', 'dark', 'voltage', 'current', 'electricity', 'cable', 'blackout'],
        'severity_factors': ['exposure', 'voltage', 'location'],
        'dept': 'Electricity Department'
    },
    'parks': {
        'classes': ['broken_bench', 'damaged_tree', 'vandalism', 'broken_fence', 'playground_hazard', 'overgrown_grass'],
        'triggers': [
            'broken bench', 'damaged tree', 'fallen tree', 'broken fence', 'broken swing',
            'broken slide', 'playground damage', 'park vandalism', 'overgrown grass',
            'park light', 'garden waste', 'fountain broken'
        ],
        'hints': ['park', 'garden', 'tree', 'bench', 'playground', 'swing', 'slide', 'grass', 'lawn', 'fountain', 'greenery'],
        'severity_factors': ['safety', 'usage'],
        'dept': 'Parks and Gardens'
    },
    'traffic': {
        'classes': ['traffic_signal_broken', 'sign_missing', 'road_marking_faded', 'illegal_parking', 'traffic_congestion'],
        'triggers': [
            'traffic light', 'traffic signal', 'signal broken', 'zebra crossing', 'road sign',
            'sign missing', 'road marking', 'illegal parking', 'traffic jam', 'no parking sign',
            'speed limit sign', 'signal not working', 'traffic light broken'
        ],
        'hints': ['traffic', 'signal', 'sign', 'marking', 'junction', 'congestion', 'parking', 'bottleneck'],
        'severity_factors': ['accident_risk'],
        'dept': 'Traffic Department'
    },
    'infrastructure': {
        'classes': ['building_damage', 'bridge_damage', 'wall_collapse', 'pillar_crack', 'staircase_damage', 'public_property_damage'],
        'triggers': [
            'bridge crack', 'bridge damage', 'building collapse', 'wall collapsed',
            'wall crack', 'pillar crack', 'roof collapse', 'scaffolding', 'construction hazard',
            'staircase broken', 'handrail broken', 'public building damage', 'compound wall'
        ],
        'hints': ['bridge', 'building', 'wall', 'pillar', 'structure', 'foundation', 'concrete', 'roof', 'railing'],
        'severity_factors': ['public_safety', 'scale'],
        'dept': 'Municipal Corporation'
    }
}

# Weights
_W_TRIGGER = 10  # Strong signal — unique to this category
_W_HINT    = 3   # Weak signal — could belong to multiple categories
_W_SUBCLASS = 15 # Very strong — exact subclass match in description or object label


def classify_issue_type(description: str, detected_objects: list):
    """
    Classify civic issue using a tiered keyword scoring system.

    Returns (category, subclass, confidence_pct)
    """
    description = (description or "").strip().lower()
    obj_labels  = [o.get('label', '').lower().replace('_', ' ') for o in detected_objects]
    # Combine description + object labels for matching
    combined    = description + " " + " ".join(obj_labels)

    scores        = {}
    best_subclass = {}

    for category, cfg in CIVIC_ISSUE_TYPES.items():
        score = 0

        # --- Trigger matches (high weight) ---
        for kw in cfg['triggers']:
            if kw in combined:
                score += _W_TRIGGER

        # --- Hint matches (low weight) ---
        for kw in cfg['hints']:
            if kw in combined:
                score += _W_HINT

        scores[category] = score

        # --- Determine best subclass for this category ---
        best_cls  = cfg['classes'][0]
        best_cs   = -1
        for cls in cfg['classes']:
            cs = 0
            cls_readable = cls.replace('_', ' ')
            if cls_readable in combined:
                cs += _W_SUBCLASS
            for word in cls.split('_'):
                if len(word) > 3 and word in combined:
                    cs += 3
            if cs > best_cs:
                best_cs  = cs
                best_cls = cls
        best_subclass[category] = best_cls

    # If everything scored 0, return infrastructure as last resort
    if not scores or max(scores.values()) == 0:
        return 'infrastructure', 'public_property_damage', 40.0

    best_cat = max(scores, key=scores.get)
    sub      = best_subclass[best_cat]

    # Normalise confidence: 40–99%
    raw_conf = scores[best_cat]
    conf     = min(99.0, max(40.0, raw_conf * 4.5))   # 10 pts trigger → 45% start; 2 triggers → 90%

    return best_cat, sub, round(conf, 1)


def assess_damage_severity(issue_type, description, detected_objects):
    """
    Assess severity (1-10) based on issue type, description and detected objects
    """
    severity_score = 5
    
    issue_type_scores = {
        'roads': 6, 'water': 7, 'sanitation': 5, 
        'electricity': 8, 'parks': 3, 'traffic': 7
    }
    severity_score += issue_type_scores.get(issue_type, 5) - 5
    
    urgent_keywords = ['dangerous', 'accident', 'injury', 'emergency', 'critical', 'life', 'death']
    for kw in urgent_keywords:
        if kw in description.lower():
            severity_score += 2
    
    size_keywords = {'small': 1, 'medium': 2, 'large': 3, 'huge': 4, 'massive': 5}
    for kw, pts in size_keywords.items():
        if kw in description.lower():
            severity_score += pts
    
    for obj in detected_objects:
        label = obj.get('label', '').lower()
        if any(x in label for x in ['large', 'big', 'huge', 'major']):
            severity_score += 1
        conf = obj.get('confidence', 0)
        if conf > 80:
            severity_score += 0.5
    
    severity_score = min(10, max(1, severity_score))
    
    if severity_score >= 8:
        level = 'Critical'
    elif severity_score >= 6:
        level = 'High'
    elif severity_score >= 4:
        level = 'Medium'
    else:
        level = 'Low'
    
    return round(severity_score, 1), level


def predict_issue_hotspots(issues, location_data):
    """
    Predict which geographic areas are likely to have issues
    Based on historical patterns and time-based trends
    """
    if not issues:
        return []
    
    location_counts = defaultdict(lambda: {'count': 0, 'types': defaultdict(int), 'recency': []})
    
    for issue in issues:
        loc = issue.get('location', '')[:30]
        if not loc:
            continue
        
        location_counts[loc]['count'] += 1
        cat = issue.get('category', 'unknown')
        location_counts[loc]['types'][cat] += 1
        
        created = issue.get('created_at')
        if created:
            days_ago = (datetime.now() - created).days
            location_counts[loc]['recency'].append(days_ago)
    
    hotspots = []
    for loc, data in location_counts.items():
        avg_recency = sum(data['recency']) / len(data['recency']) if data['recency'] else 30
        
        risk_score = (data['count'] * 0.4) + (1 / (avg_recency + 1) * 20)
        
        top_types = sorted(data['types'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        hotspots.append({
            'location': loc,
            'issue_count': data['count'],
            'risk_score': round(risk_score, 1),
            'top_categories': [t[0] for t in top_types],
            'avg_days_between': round(avg_recency, 1),
            'recommendation': 'High priority' if risk_score > 10 else 'Monitor'
        })
    
    return sorted(hotspots, key=lambda x: x['risk_score'], reverse=True)[:10]


def find_similar_issues_advanced(issues, description, location, category, threshold=0.6):
    """
    Advanced similar issue detection using multiple factors
    """
    if not issues:
        return []
    
    text_keywords = set(description.lower().split())
    
    similar = []
    for issue in issues:
        score = 0
        
        if issue.get('category') == category:
            score += 0.3
        
        issue_loc = issue.get('location', '')[:20]
        if location[:20] == issue_loc:
            score += 0.4
        
        issue_text = issue.get('issue', '').lower()
        issue_words = set(issue_text.split())
        text_overlap = len(text_keywords & issue_words) / max(len(text_keywords), 1)
        score += text_overlap * 0.3
        
        if score >= threshold:
            similar.append({
                'id': str(issue.get('id', '')),
                'issue': issue.get('issue', '')[:60],
                'location': issue.get('location', ''),
                'status': issue.get('status', ''),
                'similarity': round(score * 100, 1)
            })
    
    return sorted(similar, key=lambda x: x['similarity'], reverse=True)[:5]


def calculate_priority_score(severity, category, upvotes, days_open, sentiment_score):
    """
    Calculate priority score (1-100) considering multiple factors
    """
    base_score = {
        'Critical': 90, 'High': 70, 'Medium': 50, 'Low': 30
    }.get(severity, 50)
    
    category_priority = {
        'electricity': 15, 'roads': 12, 'water': 10,
        'sanitation': 8, 'traffic': 8, 'parks': 5
    }
    base_score += category_priority.get(category, 0)
    
    base_score += min(upvotes * 2, 20)
    
    if days_open > 30:
        base_score += 15
    elif days_open > 14:
        base_score += 10
    elif days_open > 7:
        base_score += 5
    
    base_score += sentiment_score * 15
    
    return min(100, max(1, int(base_score)))


def estimate_resolution_time(issue_type, severity, category, dept_workload=1.0):
    """
    Estimate realistic resolution time in days
    """
    base_times = {
        'roads': {'Low': 3, 'Medium': 7, 'High': 14, 'Critical': 21},
        'water': {'Low': 2, 'Medium': 5, 'High': 10, 'Critical': 14},
        'sanitation': {'Low': 1, 'Medium': 3, 'High': 7, 'Critical': 10},
        'electricity': {'Low': 1, 'Medium': 3, 'High': 7, 'Critical': 10},
        'parks': {'Low': 5, 'Medium': 10, 'High': 14, 'Critical': 21},
        'traffic': {'Low': 2, 'Medium': 5, 'High': 7, 'Critical': 10}
    }
    
    base = base_times.get(issue_type, {}).get(severity, 7)
    
    estimated_days = base * dept_workload
    
    return {
        'min_days': max(1, int(estimated_days * 0.7)),
        'max_days': int(estimated_days * 1.3),
        'avg_days': int(estimated_days),
        'confidence': 'High' if base <= 7 else 'Medium'
    }


def analyze_resolution_trends(issues, time_window_days=30):
    """
    Analyze resolution patterns for insights
    """
    if not issues:
        return {'error': 'No issues to analyze'}
    
    now = datetime.now()
    recent_issues = [i for i in issues if i.get('created_at') and 
                     (now - i.get('created_at')).days <= time_window_days]
    
    if not recent_issues:
        return {'error': 'No recent issues'}
    
    resolved = [i for i in recent_issues if 'Resolved' in (i.get('status') or '')]
    
    resolution_times = []
    for issue in resolved:
        created = issue.get('created_at')
        if created and hasattr(issue, 'resolved_at') and issue.resolved_at:
            days = (issue.resolved_at - created).days
            resolution_times.append(days)
    
    avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    category_stats = defaultdict(lambda: {'total': 0, 'resolved': 0})
    for issue in recent_issues:
        cat = issue.get('category', 'unknown')
        category_stats[cat]['total'] += 1
        if 'Resolved' in (issue.get('status') or ''):
            category_stats[cat]['resolved'] += 1
    
    resolution_rates = {}
    for cat, stats in category_stats.items():
        rate = (stats['resolved'] / stats['total'] * 100) if stats['total'] > 0 else 0
        resolution_rates[cat] = round(rate, 1)
    
    return {
        'resolution_rate': round(len(resolved) / len(recent_issues) * 100, 1),
        'avg_resolution_days': round(avg_resolution, 1),
        'total_issues': len(recent_issues),
        'resolved_count': len(resolved),
        'category_performance': resolution_rates,
        'recommendation': 'Improve resolution time' if avg_resolution > 10 else 'Good performance'
    }


def generate_insights(issues):
    """
    Generate actionable insights from issue data
    """
    if not issues:
        return []
    
    insights = []
    
    open_issues = [i for i in issues if 'Resolved' not in (i.get('status') or '')]
    if len(open_issues) > 50:
        insights.append({
            'type': 'alert',
            'title': 'High Backlog',
            'message': f'{len(open_issues)} issues pending - consider resource allocation'
        })
    
    category_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    for issue in issues:
        category_counts[issue.get('category', 'unknown')] += 1
        severity_counts[issue.get('severity', 'unknown')] += 1
    
    if category_counts:
        top_cat = max(category_counts, key=category_counts.get)
        insights.append({
            'type': 'trend',
            'title': 'Most Common Issue',
            'message': f'{top_cat} accounts for {category_counts[top_cat]} issues ({category_counts[top_cat]/len(issues)*100:.0f}%)'
        })
    
    if severity_counts.get('High', 0) + severity_counts.get('Critical', 0) > 10:
        insights.append({
            'type': 'warning',
            'title': 'Multiple High Severity Issues',
            'message': 'Immediate attention needed for critical issues'
        })
    
    return insights