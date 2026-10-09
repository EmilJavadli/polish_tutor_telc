"""Two-call validated lesson generation."""
import datetime as dt,json,re
from typing import TypeVar
from pydantic import BaseModel,ValidationError
from agent.llm import chat_json
from agent.prompts import CORE_SYSTEM,CORE_USER,PRACTICE_SYSTEM,PRACTICE_USER,VOCAB_NEW,VOCAB_REVIEW,fill
from agent.schemas import CoreLesson,Practice,Lesson
from config import EXERCISE_COMPOSITION,LISTENING_TASKS,MAX_GENERATION_ATTEMPTS,MAX_KNOWN_WORDS_IN_PROMPT,NEW_WORDS_PER_LESSON,QUIZ_COMPOSITION
from curriculum import GRAMMAR,SPEAKING_PART_NAMES,PlanDay
T=TypeVar('T',bound=BaseModel)
class LessonGenerationError(Exception):pass
def normalize(x):return re.sub(r'\s+',' ',x or '').strip().lower()
def contains_phrase(text,phrase):return re.search(rf'(?<!\w){re.escape(normalize(phrase))}(?!\w)',normalize(text)) is not None
def _choice(prefix,options,correct,allowed):
 p=[]
 if len(options) not in allowed:p.append(f'{prefix} has wrong option count')
 if correct is None or not 0<=correct<len(options):p.append(f'{prefix} has invalid correct_option')
 return p
def validate_core(c,plan,known,week_words):
 p=[]
 if len(c.new_vocabulary)!=NEW_WORDS_PER_LESSON:p.append(f'need {NEW_WORDS_PER_LESSON} vocabulary items')
 seen=set();known={normalize(x) for x in known};week={normalize(x) for x in week_words}
 for v in c.new_vocabulary:
  k=normalize(v.polish)
  if k in seen:p.append(f'{v.polish} duplicated')
  seen.add(k)
  if plan.lesson_type=='lesson' and k in known:p.append(f'{v.polish} already known')
  if plan.lesson_type=='review' and week and k not in week:p.append(f'{v.polish} not in this week')
  if not contains_phrase(c.reading_pl,v.form_in_story):p.append(f'{v.form_in_story} absent from reading')
 if [g.id for g in c.grammar_rules]!=list(plan.grammar_ids):p.append('grammar_rules ids mismatch')
 lo,hi=plan.reading_length;n=len(c.reading_pl.split())
 if not lo*.75<=n<=hi*1.25:p.append('reading length outside target')
 if len(c.listening.tasks)!=LISTENING_TASKS:p.append('wrong listening task count')
 for t in c.listening.tasks:p+=_choice(f'listening {t.id}',t.options,t.correct_option,(2,3))
 return p
def _internal_consistency(pr):
 p=[]
 for e in pr.exercises:
  if e.type!='choice' or e.correct_option is None or not e.explanation_en:continue
  chosen=normalize(e.options[e.correct_option]);mentioned=[o for o in e.options if contains_phrase(e.explanation_en,o)]
  if len(mentioned)==1 and normalize(mentioned[0])!=chosen:p.append(f'exercise {e.id}: explanation supports {mentioned[0]}, not declared answer {e.options[e.correct_option]}')
 return p
def validate_practice(pr,plan):
 p=[];total=sum(EXERCISE_COMPOSITION.values())
 if len(pr.exercises)!=total:p.append(f'need {total} exercises')
 for sec,n in EXERCISE_COMPOSITION.items():
  if sum(e.section==sec for e in pr.exercises)!=n:p.append(f'wrong {sec} count')
 for e in pr.exercises:
  if e.type=='choice':p+=_choice(f'exercise {e.id}',e.options,e.correct_option,(2,3,4))
  elif e.prompt.count('___')!=1 or not e.accepted_answers:p.append(f'exercise {e.id} invalid gap')
 if len(pr.writing_tasks)!=2:p.append('need 2 writing tasks')
 if pr.speaking.part!=plan.speaking_part:p.append('speaking part mismatch')
 if len(pr.quiz)!=sum(QUIZ_COMPOSITION.values()):p.append('wrong quiz count')
 for q in pr.quiz:
  if q.type=='multiple_choice':p+=_choice(f'quiz {q.id}',q.options,q.correct_option,(4,))
  elif q.type=='fill_blank' and (q.question.count('___')!=1 or not q.accepted_answers):p.append(f'quiz {q.id} invalid gap')
 p+=_internal_consistency(pr);return p
def _generate(messages,model,validator,label):
 problems=[]
 for _ in range(MAX_GENERATION_ATTEMPTS):
  try:
   raw=chat_json(messages);obj=model.model_validate(raw);problems=validator(obj)
  except (ValidationError,json.JSONDecodeError) as e:problems=[str(e)];raw={}
  if not problems:return obj
  messages += [{'role':'assistant','content':json.dumps(raw,ensure_ascii=False)},{'role':'user','content':'Fix all problems and return complete JSON: '+'; '.join(problems)}]
 raise LessonGenerationError(f'Could not generate valid {label}: '+'; '.join(problems))
def build_core_messages(plan,known_words,week_words):
 gl='\n'.join(f'{g}: {GRAMMAR[g][0]} ({GRAMMAR[g][1]})' for g in plan.grammar_ids)
 vr=fill(VOCAB_REVIEW,n=NEW_WORDS_PER_LESSON,week_words=', '.join(week_words)) if plan.lesson_type=='review' else fill(VOCAB_NEW,n=NEW_WORDS_PER_LESSON)
 sys=fill(CORE_SYSTEM,text_type=plan.text_type,reading_min=plan.reading_length[0],reading_max=plan.reading_length[1],level=plan.level,n_words=NEW_WORDS_PER_LESSON,vocab_rule=vr,grammar_list=gl,listening_min=plan.listening_length[0],listening_max=plan.listening_length[1],listening_type=plan.listening_type,n_listening=LISTENING_TASKS)
 usr=fill(CORE_USER,day=plan.day,week=plan.week,phase=plan.phase,level=plan.level,theme=plan.theme_en,situation=plan.situation,lesson_type=plan.lesson_type,known_words=', '.join(known_words[-MAX_KNOWN_WORDS_IN_PROMPT:]) or '(none)')
 return [{'role':'system','content':sys},{'role':'user','content':usr}]
def build_practice_messages(plan,c):
 sys=fill(PRACTICE_SYSTEM,speaking_part=plan.speaking_part,n_ex_total=sum(EXERCISE_COMPOSITION.values()),n_ex_vocab=EXERCISE_COMPOSITION['vocabulary'],n_ex_grammar=EXERCISE_COMPOSITION['grammar'],per_rule='3 per grammar point',n_ex_le=EXERCISE_COMPOSITION['language_elements'],writing_focus=plan.writing_focus,level=plan.level,writing_min=plan.writing_length[0],writing_max=plan.writing_length[1],speaking_part_name=SPEAKING_PART_NAMES[plan.speaking_part],n_quiz=sum(QUIZ_COMPOSITION.values()),n_mc=QUIZ_COMPOSITION['multiple_choice'],n_fill=QUIZ_COMPOSITION['fill_blank'],n_open=QUIZ_COMPOSITION['open'])
 usr=fill(PRACTICE_USER,level=plan.level,theme=plan.theme_en,situation=plan.situation,reading=c.reading_pl,words=', '.join(v.polish for v in c.new_vocabulary),grammar='\n'.join(f'{g.id}: {g.title}' for g in c.grammar_rules))
 return [{'role':'system','content':sys},{'role':'user','content':usr}]
def generate_lesson(plan,known_words,week_words,progress=None):
 say=progress or (lambda x:None);say('Generating reading, vocabulary, grammar and listening...')
 core=_generate(build_core_messages(plan,known_words,week_words),CoreLesson,lambda x:validate_core(x,plan,known_words,week_words),'core lesson')
 say('Generating exercises, writing, speaking and quiz...')
 practice=_generate(build_practice_messages(plan,core),Practice,lambda x:validate_practice(x,plan),'practice')
 return Lesson(**core.model_dump(),**practice.model_dump(),day=plan.day,week=plan.week,level=plan.level,lesson_type=plan.lesson_type,theme_en=plan.theme_en,situation=plan.situation,text_type=plan.text_type,created=dt.date.today().isoformat())
