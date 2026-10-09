BAND_WEIGHT={'A1':1,'A2':2,'B1':3}
def objective_score(items,answers):
    possible=sum(BAND_WEIGHT[x['band']] for x in items);got=sum(BAND_WEIGHT[x['band']] for x in items if str(answers.get(x['id'],''))==str(x['answer']))
    return round(100*got/possible,1) if possible else 0

def classify(scores):
    overall=round(sum(scores.values())/len(scores),1)
    productive=min(scores.get('writing',0),scores.get('speaking',0));receptive=min(scores.get('reading',0),scores.get('listening',0))
    if overall>=70 and productive>=55 and receptive>=60 and scores['grammar_vocab']>=60:level='B1';start=120
    elif overall>=50 and productive>=35 and receptive>=45 and scores['grammar_vocab']>=45:level='A2';start=64
    elif overall>=25:level='A1';start=29
    else:level='A0';start=1
    strengths=[k for k,v in scores.items() if v>=65];weaknesses=[k for k,v in scores.items() if v<45]
    spread=max(scores.values())-min(scores.values());confidence=.9 if spread<30 else .7
    return {'level':level,'start_day':start,'overall':overall,'scores':scores,'strengths':strengths,'weaknesses':weaknesses,'confidence':confidence}
