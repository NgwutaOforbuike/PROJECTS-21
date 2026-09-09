import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { courses } from './data';

export default function Home(){
  return (
    <ScrollView contentContainerStyle={s.page}>
      <View style={s.top}>
        <View>
          <Text style={s.brand}>NLS BAR FINALS</Text>
          <Text style={s.hello}>Revision command centre</Text>
        </View>
        <Pressable style={s.info} onPress={()=>router.push('/about')}><Text style={s.infoText}>i</Text></Pressable>
      </View>

      <View style={s.hero}>
        <Text style={s.kicker}>EXAM MODE</Text>
        <Text style={s.heroTitle}>Practice like it is the real paper.</Text>
        <Text style={s.heroSub}>No answer reveal during the attempt. Flag difficult questions, review unanswered items and see explanations only after submission.</Text>
        <Pressable style={s.heroButton} onPress={()=>router.push({pathname:'/practice',params:{course:'Mixed Practice'}})}>
          <Text style={s.heroButtonText}>Start mixed practice</Text><Text style={s.arrow}>→</Text>
        </Pressable>
      </View>

      <View style={s.sectionHead}>
        <Text style={s.sectionTitle}>Five courses</Text>
        <Pressable onPress={()=>router.push('/courses')}><Text style={s.link}>View all</Text></Pressable>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.horizontal}>
        {courses.map(c=>(
          <Pressable key={c.id} style={s.courseCard} onPress={()=>router.push({pathname:'/practice',params:{course:c.name}})}>
            <View style={[s.courseIcon,{backgroundColor:c.accent}]}><Text style={s.courseIconText}>{c.short}</Text></View>
            <Text style={s.courseTitle}>{c.name}</Text>
            <Text style={s.courseSub}>{c.description}</Text>
          </Pressable>
        ))}
      </ScrollView>

      <Text style={s.sectionTitle}>Study tools</Text>
      <View style={s.tools}>
        <Pressable style={s.tool} onPress={()=>router.push('/courses')}>
          <View style={s.toolIcon}><Text style={s.toolEmoji}>◎</Text></View>
          <View style={{flex:1}}><Text style={s.toolTitle}>Focused practice</Text><Text style={s.toolSub}>Work course by course</Text></View><Text style={s.toolArrow}>›</Text>
        </Pressable>
        <Pressable style={s.tool} onPress={()=>router.push('/progress')}>
          <View style={s.toolIcon}><Text style={s.toolEmoji}>↗</Text></View>
          <View style={{flex:1}}><Text style={s.toolTitle}>Progress</Text><Text style={s.toolSub}>Track readiness and weak areas</Text></View><Text style={s.toolArrow}>›</Text>
        </Pressable>
      </View>

      <View style={s.tip}>
        <Text style={s.tipLabel}>EXAM RULE</Text>
        <Text style={s.tipText}>Correct answers stay hidden until you submit. This prevents false confidence from immediate feedback.</Text>
      </View>
    </ScrollView>
  );
}

const s=StyleSheet.create({
  page:{padding:20,paddingTop:48,paddingBottom:42,gap:18,backgroundColor:'#F6F7FB'},
  top:{flexDirection:'row',justifyContent:'space-between',alignItems:'center'},
  brand:{fontSize:11,fontWeight:'900',letterSpacing:1.5,color:'#2563EB'},
  hello:{fontSize:25,fontWeight:'900',color:'#101828',marginTop:3},
  info:{width:36,height:36,borderRadius:18,backgroundColor:'#fff',alignItems:'center',justifyContent:'center',borderWidth:1,borderColor:'#EAECF0'},
  infoText:{fontWeight:'900',color:'#475467'},
  hero:{backgroundColor:'#101828',borderRadius:24,padding:24,gap:10},
  kicker:{color:'#84ADFF',fontSize:11,fontWeight:'900',letterSpacing:1.3},
  heroTitle:{color:'#fff',fontSize:29,lineHeight:34,fontWeight:'900',maxWidth:310},
  heroSub:{color:'#D0D5DD',fontSize:14,lineHeight:21},
  heroButton:{marginTop:8,backgroundColor:'#fff',borderRadius:14,paddingVertical:14,paddingHorizontal:16,flexDirection:'row',justifyContent:'space-between',alignItems:'center'},
  heroButtonText:{color:'#101828',fontWeight:'900'},arrow:{fontSize:20,color:'#101828'},
  sectionHead:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginTop:2},
  sectionTitle:{fontSize:18,fontWeight:'900',color:'#101828'},link:{color:'#2563EB',fontSize:13,fontWeight:'800'},
  horizontal:{gap:12,paddingRight:8},
  courseCard:{width:210,backgroundColor:'#fff',borderRadius:18,padding:16,borderWidth:1,borderColor:'#EAECF0',gap:7},
  courseIcon:{width:44,height:44,borderRadius:13,alignItems:'center',justifyContent:'center',marginBottom:4},
  courseIconText:{color:'#fff',fontSize:11,fontWeight:'900'},
  courseTitle:{fontSize:16,fontWeight:'900',color:'#101828'},courseSub:{fontSize:12,lineHeight:17,color:'#667085'},
  tools:{gap:10},
  tool:{backgroundColor:'#fff',borderRadius:16,padding:15,flexDirection:'row',alignItems:'center',gap:12,borderWidth:1,borderColor:'#EAECF0'},
  toolIcon:{width:40,height:40,borderRadius:12,backgroundColor:'#EEF4FF',alignItems:'center',justifyContent:'center'},
  toolEmoji:{fontSize:20,color:'#2563EB'},toolTitle:{fontSize:15,fontWeight:'800',color:'#101828'},toolSub:{fontSize:12,color:'#98A2B3',marginTop:2},toolArrow:{fontSize:28,color:'#98A2B3'},
  tip:{backgroundColor:'#EFF6FF',borderRadius:16,padding:16,gap:4,borderWidth:1,borderColor:'#D1E9FF'},
  tipLabel:{fontSize:10,fontWeight:'900',letterSpacing:1.2,color:'#175CD3'},tipText:{fontSize:13,lineHeight:19,color:'#344054'}
});