import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { courses } from './data';

export default function Courses(){
  return (
    <ScrollView contentContainerStyle={s.page}>
      <View style={s.head}>
        <Text style={s.eyebrow}>SYLLABUS</Text>
        <Text style={s.title}>Your five Bar Finals courses</Text>
        <Text style={s.sub}>Choose a course to enter a focused practice session. Your answers remain hidden until you submit.</Text>
      </View>
      {courses.map((c, i) => (
        <Pressable key={c.id} style={s.card} onPress={() => router.push({pathname:'/practice', params:{course:c.name}})}>
          <View style={[s.badge,{backgroundColor:c.accent}]}><Text style={s.badgeText}>{c.short}</Text></View>
          <View style={s.cardBody}>
            <Text style={s.cardTitle}>{c.name}</Text>
            <Text style={s.cardSub}>{c.description}</Text>
            <Text style={s.meta}>{i+1}/5 course module · Focus practice</Text>
          </View>
          <Text style={s.chev}>›</Text>
        </Pressable>
      ))}
      <Pressable style={s.mixed} onPress={() => router.push({pathname:'/practice',params:{course:'Mixed Practice'}})}>
        <Text style={s.mixedTitle}>Mixed practice</Text>
        <Text style={s.mixedSub}>Questions across all five courses</Text>
      </Pressable>
    </ScrollView>
  );
}

const s=StyleSheet.create({
  page:{padding:20,paddingBottom:44,gap:14,backgroundColor:'#F6F7FB'},
  head:{paddingTop:8,paddingBottom:10,gap:7},
  eyebrow:{fontSize:12,fontWeight:'800',letterSpacing:1.4,color:'#2563EB'},
  title:{fontSize:30,lineHeight:36,fontWeight:'900',color:'#101828'},
  sub:{fontSize:15,lineHeight:22,color:'#667085'},
  card:{backgroundColor:'#fff',borderRadius:18,padding:16,flexDirection:'row',alignItems:'center',gap:14,borderWidth:1,borderColor:'#EAECF0'},
  badge:{width:50,height:50,borderRadius:14,alignItems:'center',justifyContent:'center'},
  badgeText:{color:'#fff',fontWeight:'900',fontSize:13},
  cardBody:{flex:1,gap:3},
  cardTitle:{fontSize:17,fontWeight:'800',color:'#101828'},
  cardSub:{fontSize:13,lineHeight:18,color:'#667085'},
  meta:{fontSize:11,color:'#98A2B3',marginTop:4},
  chev:{fontSize:32,color:'#98A2B3',marginLeft:4},
  mixed:{marginTop:6,backgroundColor:'#101828',borderRadius:18,padding:20,gap:4},
  mixedTitle:{fontSize:18,fontWeight:'900',color:'#fff'},
  mixedSub:{color:'#D0D5DD',fontSize:13}
});