from agent.llm import chat_json
def grade_productive(kind,text):
    if not text.strip():return 0
    prompt=f'''Assess this Polish placement {kind} from A0 through B1. Return JSON only: {{"score":0-100,"level":"A0|A1|A2|B1","comment":"short English comment"}}. Consider comprehensibility, task completion, grammar, vocabulary and coherence appropriate to the level. Learner response: {text}'''
    raw=chat_json([{'role':'user','content':prompt}])
    return max(0,min(100,float(raw.get('score',0))))
