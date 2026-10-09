import streamlit as st
from placement.test_bank import GRAMMAR_VOCAB,READING,READING_TEXT,LISTENING,LISTENING_TEXT
from placement.scoring import objective_score,classify
from placement.grader import grade_productive
from agent.tts import synthesize_speech
from agent.llm import transcribe

def _choices(items,prefix):
    out={}
    for x in items:
        v=st.radio(x['q'],range(len(x['options'])),format_func=lambda i,o=x['options']:o[i],index=None,key=prefix+x['id'])
        out[x['id']]='' if v is None else str(v)
    return out

def render(repo,profile):
    ev=repo.get_or_create();section=ev.current_section;responses=dict(ev.responses or {})
    st.title('Polish placement evaluation');st.caption('Your progress is saved after each section.')
    if section=='grammar_vocab':
        with st.form('placement_g'):
            ans=_choices(GRAMMAR_VOCAB,'pg_')
            if st.form_submit_button('Continue',type='primary'):
                repo.save_section(ev.id,section,ans,'reading');st.rerun()
    elif section=='reading':
        st.markdown(READING_TEXT)
        with st.form('placement_r'):
            ans=_choices(READING,'pr_')
            if st.form_submit_button('Continue',type='primary'):
                repo.save_section(ev.id,section,ans,'listening');st.rerun()
    elif section=='listening':
        st.write('Listen and answer the questions.');audio=st.session_state.get('placement_audio')
        if not audio and st.button('Create placement audio'):
            st.session_state.placement_audio=synthesize_speech(LISTENING_TEXT);st.rerun()
        if audio:st.audio(audio,format='audio/mpeg')
        with st.form('placement_l'):
            ans=_choices(LISTENING,'pl_')
            if st.form_submit_button('Continue',type='primary'):
                repo.save_section(ev.id,section,ans,'writing');st.rerun()
    elif section=='writing':
        st.write('Write about yourself, life in Poland, a normal week, and one past or future plan.')
        text=st.text_area('Your Polish text',height=220)
        if st.button('Save and continue',type='primary'):
            repo.save_section(ev.id,section,{'text':text},'speaking');st.rerun()
    elif section=='speaking':
        st.write('Introduce yourself, describe a normal day, and mention one past experience or future plan.')
        rec=st.audio_input('Record your answer');typed=st.text_area('Or type what you would say')
        if st.button('Complete evaluation',type='primary'):
            speech=transcribe(rec.getvalue()) if rec else typed
            repo.save_section(ev.id,section,{'transcript':speech},'complete')
            allr={**responses,'speaking':{'transcript':speech}}
            scores={'grammar_vocab':objective_score(GRAMMAR_VOCAB,allr.get('grammar_vocab',{})),'reading':objective_score(READING,allr.get('reading',{})),'listening':objective_score(LISTENING,allr.get('listening',{})),'writing':grade_productive('writing',allr.get('writing',{}).get('text','')),'speaking':grade_productive('speaking',speech)}
            result=classify(scores)
            mins=st.session_state.get('daily_minutes',60);target=st.session_state.get('target_level','B1')
            repo.finish(ev.id,result,mins,target);st.session_state.placement_result=result;st.rerun()
    elif section=='complete':st.rerun()
