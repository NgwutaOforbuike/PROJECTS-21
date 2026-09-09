import React,{useMemo,useState} from 'react';
import {ScrollView,View,Text,Pressable,Alert,StyleSheet} from 'react-native';
import {useLocalSearchParams,router} from 'expo-router';
import {getQuestions} from './data';

export default function Practice(){
  const {course}=useLocalSearchParams<{course?:string}>();
  const courseName=typeof course==='string'?course:'Mixed Practice';
  const [answers,setAnswers]=useState<Record<string,number>>({});
  const [flag,setFlag]=useState<Record<string,boolean>>({});
  const [submitted,setSubmitted]=useState(false);
  const [current,setCurrent]=useState(0);
  const qs=useMemo(()=>getQuestions(courseName).map(q=>({...q,opts:[...q.opts]})),[courseName]);
  const q=qs[current];
  const answered=Object.keys(answers).filter(id=>qs.some(x=>x.id===id)).length;
  const flagged=Object.values(flag).filter(Boolean).length;
  const score=qs.reduce((n,item)=>n+(answers[item.id]===item.correct?1:0),0);

  const finish=()=>{
    const unanswered=qs.filter(item=>answers[item.id]===undefined).length;
    if(unanswered){
      Alert.alert('Submit attempt?',`You still have ${unanswered} unanswered question(s).`,[
        {text:'Keep reviewing',style:'cancel'},
        {text:'Submit',style:'destructive',onPress:()=>setSubmitted(true)}
      ]);
    } else setSubmitted(true);
  };

  if(!q) return <View style={s.empty}><Text style={s.title}>No questions available</Text><Pressable onPress={()=>router.back()}><Text style={s.link}>Return</Text></Pressable></View>;

  if(submitted){
    const pct=Math.round((score/qs.length)*100);
    return <ScrollView contentContainerStyle={s.page}>
      <View style={s.resultHero}>
        <Text style={s.resultLabel}>ATTEMPT COMPLETE</Text>
        <Text style={s.score}>{score}/{qs.length}</Text>
        <Text style={s.percent}>{pct}%</Text>
        <Text style={s.resultSub}>{courseName}</Text>
      </View>
      <View style={s.statRow}>
        <View style={s.stat}><Text style={s.statNum}>{score}</Text><Text style={s.statText}>Correct</Text></View>
        <View style={s.stat}><Text style={s.statNum}>{qs.length-score}</Text><Text style={s.statText}>Incorrect</Text></View>
        <View style={s.stat}><Text style={s.statNum}>{flagged}</Text><Text style={s.statText}>Flagged</Text></View>
      </View>
      <Text style={s.sectionTitle}>Review answers</Text>
      {qs.map((item,idx)=>{
        const ok=answers[item.id]===item.correct;
        return <View key={item.id} style={s.reviewCard}>
          <Text style={s.reviewNo}>QUESTION {idx+1}</Text>
          <Text style={s.reviewStem}>{item.stem}</Text>
          <View style={[s.feedback,ok?s.feedbackGood:s.feedbackBad]}>
            <Text style={s.feedbackTitle}>{ok?'Correct':'Incorrect'}</Text>
            <Text style={s.feedbackBody}>Correct answer: {String.fromCharCode(65+item.correct)}. {item.opts[item.correct]}</Text>
          </View>
          <Text style={s.explanation}>{item.exp}</Text>
        </View>
      })}
      <Pressable style={s.primary} onPress={()=>router.replace('/')}><Text style={s.primaryText}>Return to dashboard</Text></Pressable>
      <Pressable style={s.secondary} onPress={()=>{setAnswers({});setFlag({});setSubmitted(false);setCurrent(0);}}><Text style={s.secondaryText}>Try again</Text></Pressable>
    </ScrollView>;
  }

  return <View style={s.screen}>
    <View style={s.header}>
      <View style={s.headerTop}><View style={{flex:1}}><Text style={s.course}>{courseName}</Text><Text style={s.counter}>Question {current+1} of {qs.length}</Text></View><Pressable style={s.flagButton} onPress={()=>setFlag(f=>({...f,[q.id]:!f[q.id]}))}><Text style={s.flagText}>{flag[q.id]?'⚑ Flagged':'⚐ Flag'}</Text></Pressable></View>
      <View style={s.progressTrack}><View style={[s.progressFill,{width:`${((current+1)/qs.length)*100}%`}]} /></View>
    </View>

    <ScrollView contentContainerStyle={s.questionArea}>
      <Text style={s.stem}>{q.stem}</Text>
      <View style={s.options}>
        {q.opts.map((o,i)=>{
          const selected=answers[q.id]===i;
          return <Pressable key={i} onPress={()=>setAnswers(a=>({...a,[q.id]:i}))} style={[s.opt,selected&&s.selected]}>
            <View style={[s.letter,selected&&s.letterSelected]}><Text style={[s.letterText,selected&&s.letterTextSelected]}>{String.fromCharCode(65+i)}</Text></View>
            <Text style={s.optText}>{o}</Text>
          </Pressable>;
        })}
      </View>
      <Text style={s.hiddenNote}>Correctness is hidden until final submission.</Text>
    </ScrollView>

    <View style={s.bottom}>
      <View style={s.bottomMeta}><Text style={s.metaText}>{answered}/{qs.length} answered</Text><Text style={s.metaText}>{flagged} flagged</Text></View>
      <View style={s.actions}>
        <Pressable disabled={current===0} style={[s.navButton,current===0&&s.disabled]} onPress={()=>setCurrent(i=>Math.max(0,i-1))}><Text style={s.navText}>Back</Text></Pressable>
        {current<qs.length-1?
          <Pressable style={s.nextButton} onPress={()=>setCurrent(i=>Math.min(qs.length-1,i+1))}><Text style={s.nextText}>Next question</Text></Pressable>:
          <Pressable style={s.submitButton} onPress={finish}><Text style={s.nextText}>Submit attempt</Text></Pressable>}
      </View>
    </View>
  </View>;
}

const s=StyleSheet.create({
  screen:{flex:1,backgroundColor:'#F6F7FB'},page:{padding:20,paddingBottom:42,gap:14,backgroundColor:'#F6F7FB'},
  empty:{flex:1,alignItems:'center',justifyContent:'center',gap:12},title:{fontSize:24,fontWeight:'900'},link:{color:'#2563EB',fontWeight:'800'},
  header:{paddingHorizontal:20,paddingTop:10,paddingBottom:14,backgroundColor:'#F6F7FB'},headerTop:{flexDirection:'row',alignItems:'center',gap:12},
  course:{fontSize:15,fontWeight:'900',color:'#101828'},counter:{fontSize:12,color:'#667085',marginTop:3},
  flagButton:{paddingVertical:9,paddingHorizontal:12,backgroundColor:'#fff',borderRadius:12,borderWidth:1,borderColor:'#EAECF0'},flagText:{fontSize:12,fontWeight:'800',color:'#475467'},
  progressTrack:{height:5,backgroundColor:'#E4E7EC',borderRadius:4,marginTop:14,overflow:'hidden'},progressFill:{height:5,backgroundColor:'#2563EB',borderRadius:4},
  questionArea:{padding:20,paddingTop:18,paddingBottom:130},stem:{fontSize:22,lineHeight:31,fontWeight:'800',color:'#101828',marginBottom:20},
  options:{gap:12},opt:{backgroundColor:'#fff',borderRadius:16,padding:15,flexDirection:'row',alignItems:'center',gap:12,borderWidth:1.5,borderColor:'#EAECF0'},
  selected:{borderColor:'#2563EB',backgroundColor:'#F5F8FF'},letter:{width:34,height:34,borderRadius:17,backgroundColor:'#F2F4F7',alignItems:'center',justifyContent:'center'},
  letterSelected:{backgroundColor:'#2563EB'},letterText:{fontWeight:'900',color:'#475467'},letterTextSelected:{color:'#fff'},optText:{flex:1,fontSize:15,lineHeight:21,color:'#344054'},
  hiddenNote:{fontSize:12,color:'#98A2B3',textAlign:'center',marginTop:18},
  bottom:{position:'absolute',bottom:0,left:0,right:0,padding:16,paddingBottom:22,backgroundColor:'#fff',borderTopWidth:1,borderTopColor:'#EAECF0'},
  bottomMeta:{flexDirection:'row',justifyContent:'space-between',marginBottom:10},metaText:{fontSize:11,color:'#667085',fontWeight:'700'},
  actions:{flexDirection:'row',gap:10},navButton:{paddingHorizontal:20,paddingVertical:15,borderRadius:13,backgroundColor:'#F2F4F7'},disabled:{opacity:.4},navText:{fontWeight:'800',color:'#344054'},
  nextButton:{flex:1,padding:15,borderRadius:13,backgroundColor:'#2563EB'},submitButton:{flex:1,padding:15,borderRadius:13,backgroundColor:'#101828'},nextText:{color:'#fff',fontWeight:'900',textAlign:'center'},
  resultHero:{backgroundColor:'#101828',borderRadius:24,padding:28,alignItems:'center',gap:3,marginTop:4},resultLabel:{color:'#84ADFF',fontSize:11,fontWeight:'900',letterSpacing:1.2},
  score:{fontSize:46,fontWeight:'900',color:'#fff',marginTop:7},percent:{fontSize:19,fontWeight:'800',color:'#D0D5DD'},resultSub:{fontSize:12,color:'#98A2B3',marginTop:4},
  statRow:{flexDirection:'row',gap:10},stat:{flex:1,backgroundColor:'#fff',borderRadius:15,padding:15,alignItems:'center',borderWidth:1,borderColor:'#EAECF0'},statNum:{fontSize:22,fontWeight:'900',color:'#101828'},statText:{fontSize:10,color:'#98A2B3',marginTop:3},
  sectionTitle:{fontSize:18,fontWeight:'900',color:'#101828',marginTop:7},reviewCard:{backgroundColor:'#fff',borderRadius:17,padding:17,gap:9,borderWidth:1,borderColor:'#EAECF0'},
  reviewNo:{fontSize:10,fontWeight:'900',letterSpacing:1.1,color:'#667085'},reviewStem:{fontSize:15,lineHeight:21,fontWeight:'800',color:'#101828'},
  feedback:{padding:12,borderRadius:12,gap:3},feedbackGood:{backgroundColor:'#ECFDF3'},feedbackBad:{backgroundColor:'#FEF3F2'},feedbackTitle:{fontWeight:'900',fontSize:13},feedbackBody:{fontSize:12,lineHeight:18,color:'#344054'},explanation:{fontSize:12,lineHeight:18,color:'#667085'},
  primary:{padding:16,borderRadius:14,backgroundColor:'#2563EB',marginTop:4},primaryText:{color:'#fff',fontWeight:'900',textAlign:'center'},secondary:{padding:15,borderRadius:14,backgroundColor:'#fff',borderWidth:1,borderColor:'#D0D5DD'},secondaryText:{fontWeight:'800',textAlign:'center',color:'#344054'}
});