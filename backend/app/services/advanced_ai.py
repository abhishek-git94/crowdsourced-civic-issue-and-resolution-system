from datetime import datetime, timedelta
from collections import defaultdict
import random


SENTIMENT_KEYWORDS = {
    'urgent': ['immediately', 'urgent', 'emergency', 'dangerous', 'unsafe', 'critical', 'life threatening', 'accident', 'injury'],
    'concerned': ['worried', 'concerned', 'disappointed', 'frustrated', 'annoyed', 'upset', 'fed up'],
    'normal': ['please', 'request', 'kindly', 'hope', 'could', 'would be nice'],
    'angry': ['unacceptable', 'ridiculous', 'pathetic', 'worst', 'shameful', 'complaint', 'absolutely']
}

DEPT_SCORES = {
    'Public Works Department (PWD)': {'roads': 95, 'pothole': 90, 'infrastructure': 85, 'bridge': 90, 'footpath': 80},
    'Sanitation Department': {'garbage': 95, 'waste': 90, 'litter': 85, 'dirty': 80, 'trash': 90},
    'Water Department': {'water': 95, 'leak': 90, 'drainage': 85, 'flooding': 80, 'overflow': 85},
    'Electricity Department': {'electricity': 95, 'power': 90, 'light': 85, 'wire': 90, 'pole': 80},
    'Parks and Gardens': {'parks': 95, 'garden': 90, 'trees': 85, 'greenery': 80, 'grass': 85},
    'Traffic Department': {'traffic': 95, 'signal': 90, 'sign': 85, 'parking': 80, 'road_marking': 85},
    'Health Department': {'health': 95, 'medical': 90, 'hospital': 85, 'disease': 80, ' sanitation': 90},
    'Fire Department': {'fire': 95, 'burning': 90, 'smoke': 85, 'gas': 80, 'hazard': 90}
}

RESOLUTION_BASELINE = {
    'roads': 7, 'pothole': 3, 'garbage': 2, 'water': 5, 'electricity': 1,
    'parks': 5, 'traffic': 3, 'health': 7, 'infrastructure': 14, 'default': 7
}


def analyze_sentiment(text):
    if not text:
        return {'sentiment': 'normal', 'urgency_score': 0.5}
    
    text_lower = text.lower()
    scores = {'urgent': 0, 'concerned': 0, 'normal': 0, 'angry': 0}
    
    for category, keywords in SENTIMENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[category] += 1
    
    max_score = max(scores.values())
    if max_score == 0:
        sentiment = 'normal'
    else:
        sentiment = max(scores, key=scores.get)
    
    urgency_score = min(1.0, (scores['urgent'] * 0.4 + scores['angry'] * 0.3 + scores['concerned'] * 0.2))
    
    return {
        'sentiment': sentiment,
        'urgency_score': urgency_score,
        'detected_keywords': [kw for kw in sum(SENTIMENT_KEYWORDS.values(), []) if kw in text_lower]
    }


def smart_assign_department(category, description, detected_objects):
    if not category:
        return 'Municipal Corporation', 0.5
    
    category_lower = category.lower()
    combined_text = f"{category_lower} {description or ''} {' '.join([o.get('label', '') for o in detected_objects])}"
    
    best_dept = 'Municipal Corporation'
    best_score = 0.5
    
    for dept, keywords in DEPT_SCORES.items():
        score = 0
        for kw, pts in keywords.items():
            if kw in combined_text:
                score += pts
        
        if score > best_score:
            best_score = score / 100
            best_dept = dept
    
    return best_dept, best_score


def predict_resolution_days(category, severity, dept_workload_factor=1.0):
    if not category:
        return RESOLUTION_BASELINE['default']
    
    category_lower = category.lower()
    base_days = RESOLUTION_BASELINE.get(category_lower, RESOLUTION_BASELINE['default'])
    
    severity_multiplier = {'Low': 1.0, 'Medium': 1.3, 'High': 1.6, 'Urgent': 2.0}
    sev_mult = severity_multiplier.get(severity, 1.0)
    
    predicted_days = base_days * sev_mult * dept_workload_factor
    
    return max(1, min(30, int(predicted_days)))


def cluster_issues(issues, similarity_threshold=0.7):
    clusters = []
    used_indices = set()
    
    for i, issue in enumerate(issues):
        if i in used_indices:
            continue
        
        cluster = [issue]
        used_indices.add(i)
        
        issue_emb = issue.get('embedding') if hasattr(issue, 'embedding') else None
        if not issue_emb:
            continue
            
        for j, other in enumerate(issues[i+1:], start=i+1):
            if j in used_indices:
                continue
            
            other_emb = other.get('embedding') if hasattr(other, 'embedding') else None
            if not other_emb:
                continue
            
            try:
                from ..utils.duplicate_detector import cosine_similarity, json_to_embed
                emb1 = json_to_embed(issue_emb)
                emb2 = json_to_embed(other_emb)
                if emb1 and emb2:
                    sim = cosine_similarity(emb1, emb2)
                    if sim >= similarity_threshold:
                        cluster.append(other)
                        used_indices.add(j)
            except:
                continue
        
        if len(cluster) > 1:
            clusters.append({
                'cluster_id': len(clusters),
                'issues': cluster,
                'count': len(cluster),
                'representative': cluster[0]
            })
    
    return clusters


def detect_anomalies(issues, time_window_days=7, spike_threshold=2.5):
    now = datetime.now()
    daily_counts = defaultdict(int)
    location_counts = defaultdict(int)
    category_counts = defaultdict(int)
    
    for issue in issues:
        created = getattr(issue, 'created_at', None)
        if not created:
            continue
        
        days_ago = (now - created).days
        if days_ago <= time_window_days:
            daily_counts[days_ago] += 1
            loc = getattr(issue, 'location', 'unknown')
            location_counts[loc[:20] if loc else 'unknown'] += 1
            cat = getattr(issue, 'category', 'unknown')
            category_counts[cat] += 1
    
    avg_daily = sum(daily_counts.values()) / max(1, len(daily_counts))
    anomalies = []
    
    for day, count in daily_counts.items():
        if count > avg_daily * spike_threshold:
            anomalies.append({
                'type': 'spike',
                'day': day,
                'count': count,
                'avg_expected': round(avg_daily, 1),
                'severity': 'high' if count > avg_daily * 3 else 'medium'
            })
    
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        if count >= 5:
            anomalies.append({
                'type': 'location_spike',
                'location': loc,
                'count': count,
                'severity': 'high' if count >= 10 else 'medium'
            })
    
    return {
        'anomalies': anomalies,
        'total_issues': len(issues),
        'daily_average': round(avg_daily, 1),
        'location_hotspots': sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    }


def natural_language_query(issues, query):
    query_lower = query.lower()
    
    results = {
        'type': 'general',
        'filters': {},
        'summary': ''
    }
    
    if any(w in query_lower for w in ['high', 'urgent', 'priority']):
        results['filters']['priority'] = ['High', 'Urgent']
        results['type'] = 'priority'
    
    if any(w in query_lower for w in ['water', 'drainage', 'leak', 'flood']):
        results['filters']['category'] = ['water', 'drainage']
        results['type'] = 'category'
    
    if any(w in query_lower for w in ['pending', 'not resolved', 'open']):
        results['filters']['status'] = ['Pending']
        results['type'] = 'status'
    
    if any(w in query_lower for w in ['this week', 'recent', 'last 7']):
        results['time_filter'] = 7
        results['type'] = 'time'
    
    if 'resolved' in query_lower and 'this month' in query_lower:
        results['time_filter'] = 30
        results['filters']['status'] = ['Resolved', 'Resolved (Unconfirmed)']
        results['type'] = 'resolution_rate'
    
    if any(w in query_lower for w in ['most', 'top', 'worst']):
        if 'location' in query_lower or 'area' in query_lower:
            results['type'] = 'location_ranking'
    
    filtered = issues
    if 'priority' in results['filters']:
        filtered = [i for i in filtered if getattr(i, 'priority', 'Low') in results['filters']['priority']]
    if 'status' in results['filters']:
        filtered = [i for i in filtered if getattr(i, 'status', '') in results['filters']['status']]
    if 'category' in results['filters']:
        filtered = [i for i in filtered if any(c in (getattr(i, 'category', '') or '').lower() for c in results['filters']['category'])]
    if 'time_filter' in results:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=results['time_filter'])
        filtered = [i for i in filtered if getattr(i, 'created_at', None) and i.created_at >= cutoff]
    
    results['count'] = len(filtered)
    results['issues'] = filtered[:20]
    
    return results